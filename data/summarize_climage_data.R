# Load required libraries
library(dplyr)
library(lubridate)

# Read the CSV file
data <- read.csv("./CSSRI_IMD_daily_2018.csv")

# Ensure the 'Date' column exists and convert it to Date format
if (!"DATE" %in% colnames(data)) {
  stop("The dataset must contain a 'DATE' column in YYYY-MM-DD format.")
}
data <- data %>%
  mutate(DATE = as.Date(DATE, format = "%Y-%m-%d"))

# Add dekadal and monthly columns
data <- data %>%
  mutate(
    YEAR = year(DATE),
    MONTH = month(DATE),
    DEKAD = case_when(
      day(DATE) <= 10 ~ 1,
      day(DATE) <= 20 ~ 2,
      TRUE ~ 3
    )
  )

# Create a grouping column for dekadals
data <- data %>%
mutate(DEKOY = paste(YEAR, sprintf("%02d", MONTH), sprintf("%02d", DEKAD), sep = "-"))

# Calculate dekadal summaries
dekadal_summary <- data %>%
  group_by(DEKOY) %>%
  summarise(across(where(is.numeric), list(mean = mean, sum = sum, sd = sd), na.rm = TRUE))

# Add a grouping column for monthly summaries
data <- data %>%
mutate(MOY = paste(YEAR, sprintf("%02d", MONTH), sep = "-"))

# Calculate monthly summaries
monthly_summary <- data %>%
  group_by(MOY) %>%
  summarise(across(where(is.numeric), list(mean = mean, sum = sum, sd = sd), na.rm = TRUE))

# Save the summaries to CSV files
write.csv(dekadal_summary, "dekadal_summary.csv", row.names = FALSE)
write.csv(monthly_summary, "monthly_summary.csv", row.names = FALSE)

# Print summaries
print("Dekadal Summary:")
print(dekadal_summary)
print("Monthly Summary:")
print(monthly_summary)
