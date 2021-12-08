# # # # # # # # # # # # # # # # # # # # #
# This script creates a Kaplan-Meier plots for the study outcomes
# # # # # # # # # # # # # # # # # # # # #

# Preliminaries ----

## Import libraries ----
library('tidyverse')
library('here')
library('glue')
library('survival')

## Import custom user functions from lib
source(here::here("analysis", "lib", "utility_functions.R"))
source(here::here("analysis", "lib", "redaction_functions.R"))
source(here::here("analysis", "lib", "survival_functions.R"))

date_cols <- c(
  "date_antigen_negative",
  "date_exposure_to_disease",
  "date_historic_covid",
  "date_potential_historic_covid",
  "date_probable_covid",
  "date_probable_covid_pos_test",
  "date_probable_covid_sequelae",
  "date_suspected_covid_advice",
  "date_suspected_covid_had_test",
  "date_suspected_covid_isolation",
  "date_suspected_covid_nonspecific",
  "date_suspected_covid",
  "date_covid_unrelated_to_case_status",
  "date_sgss_positive_test",
  "date_died_ons"
)


## create output directory ----
fs::dir_create(here("output"))

## custom functions ----

ceiling_any <- function(x, to=1){
  # round to nearest 100 millionth to avoid floating point errors
  ceiling(plyr::round_any(x/to, 1/100000000))*to
}


## define theme ----

plot_theme <-
  theme_minimal()+
  theme(
    legend.position = "left",
    panel.border=element_rect(colour='black', fill=NA),
    strip.text.y.right = element_text(angle = 0),
    axis.line.x = element_line(colour = "black"),
    axis.text.x = element_text(angle = 70, vjust = 1, hjust=1),
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank(),
    axis.ticks.x = element_line(colour = 'black')
  )


## Import processed data ----

data_cohort <- read_csv(here::here("output", "input.csv")) %>%
  mutate(across(starts_with("date"),  as.Date))

# derive start and end dates
minmax <- data_cohort %>%   
    mutate(group="group") %>% 
    group_by(group) %>% 
    summarise(max=max(c_across(all_of(date_cols)),na.rm = T),
              min=min(c_across(all_of(date_cols)),na.rm = T)) %>%
    select(-group)


data <- data_cohort %>%
    mutate(start_date=minmax$min,
            end_date=minmax$max)

data_tte <- data %>%
  transmute(
    patient_id,
    date_probable_covid_pos_test,
    date_sgss_positive_test,
    date_event = pmin(
      date_died_ons,
      end_date,
      na.rm=TRUE
    ),
    indicator_death = case_when(date_died_ons<=end_date & died_ons==1~T,
                                TRUE ~ F),
    indicator_death_covid = case_when(date_died_ons<=end_date & died_ons_covid==1~T,
                                TRUE ~ F),
    indicator_death_noncovid = case_when(date_died_ons<=end_date & died_ons_noncovid==1~T,
                                TRUE ~ F),
# censor death category if end date exceeds last date
    death_category = case_when( is.na(date_died_ons)~"alive",
                                date_died_ons>end_date ~ "alive",
                                TRUE ~ death_category),
    pvetestSGSS_to_death = date_event - date_sgss_positive_test,
    pvetestPC_to_death = date_event - date_probable_covid_pos_test,
    tteSGSS = tte(date_sgss_positive_test,date_died_ons,end_date),
    indicator_death_covid_calc = censor_indicator(died_ons_covid,end_date),
    indicator_death_noncovid_calc = censor_indicator(died_ons_noncovid,end_date)
  )

## positive test as indicated in SGSS or in primary care
df_pvetestPC <- data_tte %>% 
  drop_na(date_probable_covid_pos_test)
df_pvetestSGSS <- data_tte %>% 
  drop_na(date_sgss_positive_test)

covid_deaths <- df_pvetestSGSS %>%
  transmute(group="Covid Death",
            indicator=indicator_death_covid_calc,
            tteSGSS,
            patient_id)

non_covid_deaths <- df_pvetestSGSS %>%
  transmute(group="Non-Covid Death",
            indicator=indicator_death_noncovid_calc,
            tteSGSS,
            patient_id)
 
SGSS<-non_covid_deaths %>%
  bind_rows(covid_deaths)




survobj <- function(.data, time, indicator, group_vars, threshold){

  dat_filtered <- .data %>%
    mutate(
      .time = .data[[time]],
      .indicator = .data[[indicator]]
    ) %>%
    filter(
      !is.na(.time),
      .time>0
    )

  unique_times <- unique(c(dat_filtered[[time]]))

  dat_surv <- dat_filtered %>%
    group_by(across(all_of(group_vars))) %>%
    transmute(
      .time = .data[[time]],
      .indicator = .data[[indicator]]
    )

  dat_surv1 <- dat_surv %>%
    nest() %>%
    mutate(
      n_events = map_int(data, ~sum(.x$.indicator, na.rm=TRUE)),
      surv_obj = map(data, ~{
        survfit(Surv(.time, .indicator) ~ 1, data = .x, conf.type="log-log")
      }),
      surv_obj_tidy = map(surv_obj, ~tidy_surv(.x, addtimezero = TRUE)),
    ) %>%
    select(group_vars, n_events, surv_obj_tidy) %>%
    unnest(surv_obj_tidy)

  dat_surv_rounded <- dat_surv1 %>%
    mutate(
      # Use ceiling not round. This is slightly biased upwards,
      # but means there's no disclosure risk at the boundaries (0 and 1) where masking would otherwise be threshold/2
      surv = ceiling_any(surv, 1/floor(max(n.risk, na.rm=TRUE)/(threshold+1))),
      surv.ll = ceiling_any(surv.ll, 1/floor(max(n.risk, na.rm=TRUE)/(threshold+1))),
      surv.ul = ceiling_any(surv.ul, 1/floor(max(n.risk, na.rm=TRUE)/(threshold+1))),
    )
  dat_surv_rounded
  #dat_surv1
}

get_colour_scales <- function(colour_type = "qual"){

  if(colour_type == "qual"){
    list(
      scale_color_brewer(type="qual", palette="Set1", na.value="grey"),
      scale_fill_brewer(type="qual", palette="Set1", guide="none", na.value="grey")
      #ggthemes::scale_color_colorblind(),
      #ggthemes::scale_fill_colorblind(guide=FALSE),
      #rcartocolor::scale_color_carto_d(palette = "Safe"),
      #rcartocolor::scale_fill_carto_d(palette = "Safe", guide=FALSE),
      #ggsci::scale_color_simpsons(),
      #ggsci::scale_fill_simpsons(guide=FALSE)
    )
  } else if(colour_type == "cont"){
    list(
      viridis::scale_color_viridis(discrete = FALSE, na.value="grey"),
      viridis::scale_fill_viridis(discrete = FALSE, guide = FALSE, na.value="grey")
    )
  } else if(colour_type == "ordinal"){
    list(
      viridis::scale_color_viridis(discrete = TRUE, option="D", na.value="grey"),
      viridis::scale_fill_viridis(discrete = TRUE, guide = FALSE, option="D", na.value="grey")
    )
  } else if(colour_type == "ordinal5"){
    list(
      scale_color_manual(values=viridisLite::viridis(n=5), na.value="grey"),
      scale_fill_manual(guide = FALSE, values=viridisLite::viridis(n=5), na.value="grey")
    )
  } else
    stop("colour_type '", colour_type, "' not supported -- must be 'qual', 'cont', or 'ordinal'")
}


ggplot_surv <- function(.surv_data, colour_var, colour_name, colour_type="qual", ci=FALSE, title=""){

  lines <- list(geom_step(aes(x=time, y=1-surv)))
  if(ci){
    lines <- append(lines, list(geom_rect(aes(xmin=time, xmax=leadtime, ymin=1-surv.ll, ymax=1-surv.ul), alpha=0.1, colour="transparent")))
  }

  surv_plot <- .surv_data %>%
    ggplot(aes_string(group=colour_var, colour=colour_var, fill=colour_var)) +
    lines+
    get_colour_scales(colour_type)+
    scale_x_continuous(breaks = seq(0,80,10))+
    coord_cartesian(xlim=c(0, 80))+
    labs(
      x="Days since vaccination",
      y="Event-free rate",
      colour=colour_name,
      title=NULL
    )+
    theme_minimal(base_size=9)+
    theme(
      axis.line.x = element_line(colour = "black"),
      panel.grid.minor.x = element_blank()
    )

  surv_plot
}


test_surv <- survobj(SGSS, "tteSGSS", "indicator", "group",0)
kmplot<-ggplot_surv(test_surv, "group", "", "qual", TRUE, TRUE)
ggsave(filename=here::here("output", "figsr.tiff"),kmplot,width = 10, height = 15, units = "cm")

