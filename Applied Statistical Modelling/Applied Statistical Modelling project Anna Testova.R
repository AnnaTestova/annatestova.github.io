library(dplyr)
library(ggplot2)
library(lubridate)

weather <- read.csv("~/Desktop/GlobalWeatherRepository.csv")

colnames(weather)

moscow <- weather %>% filter(location_name == "Moscow")

moscow$Date <- seq.Date(from = as.Date("2020-01-01"), by = "day", length.out = nrow(moscow))

moscow$Month <- month(moscow$Date)
moscow$Season <- case_when(
  moscow$Month %in% c(12, 1, 2) ~ "Winter",
  moscow$Month %in% c(3, 4, 5) ~ "Spring",
  moscow$Month %in% c(6, 7, 8) ~ "Summer",
  moscow$Month %in% c(9, 10, 11) ~ "Autumn"
)

moscow$RainDay <- ifelse(moscow$precip_mm > 0, "Yes", "No")

set.seed(123)  
moscow$Tourist_Visits <- round(
  100 + 3 * moscow$temperature_celsius - 20 * (moscow$RainDay == "Yes") + rnorm(nrow(moscow), 0, 10)
)

ggplot(moscow, aes(x=Season, y=temperature_celsius, fill=Season)) +
  geom_boxplot() +
  ggtitle("Temperature by Season in Moscow") +
  ylab("Temperature (°C)")

ggplot(moscow, aes(x=temperature_celsius, y=Tourist_Visits)) +
  geom_point(alpha=0.6) +
  geom_smooth(method="lm", se=FALSE, color="red") +
  ggtitle("Tourist Visits vs Temperature") +
  xlab("Temperature (°C)") + ylab("Tourist Visits")

summary(moscow$temperature_celsius)
summary(moscow$Tourist_Visits)

moscow %>% group_by(Season) %>%
  summarise(
    Mean_Temp = mean(temperature_celsius, na.rm=TRUE),
    SD_Temp = sd(temperature_celsius, na.rm=TRUE),
    Mean_Visits = mean(Tourist_Visits),
    SD_Visits = sd(Tourist_Visits),
    n = n()
  )

anova_model <- aov(temperature_celsius ~ Season, data=moscow)
summary(anova_model)

shapiro.test(residuals(anova_model))

t.test(Tourist_Visits ~ RainDay, data=moscow, var.equal=TRUE)

lm_model <- lm(Tourist_Visits ~ temperature_celsius + precip_mm, data=moscow)
summary(lm_model)

par(mfrow=c(2,2))
plot(lm_model)
