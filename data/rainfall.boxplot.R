library(dplyr)
library(tidyr)

# Read in the data
df <- read.csv("./CSSRI_daily_weather_ET0.csv")
df$MONTH <- format(as.Date(df$DATE), "%m")

df_monthly <- df %>%
  group_by(MONTH) %>%
  summarise(
    avg_et0 = 30 * mean(ETREF, na.rm = TRUE),
    avg_rain = 30 * mean(RAIN, na.rm = TRUE),
    .groups = "drop")

# Extract the necessary columns
months <- format(seq(as.Date("2021-01-01"), as.Date("2021-12-01"), by = "month"), "%b")
avg_rain <- df_monthly$avg_rain
avg_et0 <- df_monthly$avg_et0
deficit <- df_monthly$deficit


# Create the bar plot
barplot(-avg_et0, 
        beside = TRUE, 
        names.arg = months,
        col = "gray80",
        ylim = c(-300, 200),  # Set y-axis limits
        ylab = "Average Quantity (mm)",
        xlab = "Month")
barplot(avg_rain, 
        col = "gray60", 
        add = TRUE)

x_coords <- seq(0.7, by = 1.2, length.out = length(months))  # Adjust for barplot spacing

segments(x0 = x_coords - 0.5, y0 = -deficit,  # Start of the segment
         x1 = x_coords + 0.5, y1 = -deficit,  # End of the segment
         col = "black", lwd = 2)
legend("topright", 
       legend = c("Rainfall", "Referenece ET"), 
       fill = c("gray60", "gray80"))
