library(dplyr)
library(ggplot2)
library(reshape2)

dsr_current <- read.csv("./DSR_Fallow_Wheat_120_0.47_05-21/DSR_Wheat_20250211-110216.csv")
dsr_current$Planting_Date <- format(as.Date(dsr_current$Planting_Date), "%m-%d")
dsr_best <- read.csv("./DSR_Fallow_Wheat_120_0.75_05-01/DSR_Wheat_20250211-110250.csv")
dsr_best$Planting_Date <- format(as.Date(dsr_best$Planting_Date), "%m-%d")
tpr_current <- read.csv("./TPR_Fallow_Wheat_135_10mm_06-10/TPR_Wheat_20250211-115024.csv")
tpr_current$Planting_Date <- format(as.Date(tpr_current$Planting_Date), "%m-%d")
tpr_best <- read.csv("./TPR_Fallow_Wheat_120_0.75_07-01/TPR_Wheat_20250211-115112.csv")
tpr_best$Planting_Date <- format(as.Date(tpr_best$Planting_Date), "%m-%d")

# Function to calculate summary statistics (Mean ± SD) for numeric columns starting from ETref
summary_stats <- function(data, group_cols, start_col, source_name) {
  # Get column names starting from the specified column (ETref onwards)
  numeric_cols <- names(data)[which(names(data) == start_col):ncol(data)]
  
  data %>%
    group_by(across(all_of(group_cols))) %>%  # Group by specified categorical columns
    summarise(across(all_of(numeric_cols), 
                     list(mean = ~ mean(.x, na.rm = TRUE), 
                          sd = ~ sd(.x, na.rm = TRUE)), 
                     .names = "{.col}_{.fn}"), 
              .groups = "drop") %>%
    mutate(Source = source_name)  # Add a column for the source dataframe name
}

# Apply function to multiple datasets and add a 'Source' column
summary_dsr_current <- summary_stats(dsr_current, c("Planting_Date", "Crop_Type"), "ETref", "dsr_current")
summary_dsr_best <- summary_stats(dsr_best, c("Planting_Date", "Crop_Type"), "ETref", "dsr_best")
summary_tpr_current <- summary_stats(tpr_current, c("Planting_Date", "Crop_Type"), "ETref", "tpr_current")
summary_tpr_best <- summary_stats(tpr_best, c("Planting_Date", "Crop_Type"), "ETref", "tpr_best")

# Combine all summary tables into one
combined_summary <- bind_rows(summary_dsr_current, summary_dsr_best, summary_tpr_current, summary_tpr_best)

# Save the combined summary table to a single CSV file
write.csv(combined_summary, "combined_summary_mean_sd.csv", row.names = FALSE)
