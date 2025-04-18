library(dplyr)
library(reshape2)

# Read and format data
df_merged <- read.csv("./Wheat_20250205-093538.csv")
df_merged$Planting_Date <- as.Date(df_merged$Planting_Date, format = "%Y-%m-%d")
df_merged$Planting_MD <- format(df_merged$Planting_Date, "%m-%d")

# Select relevant variables
variables <- c("Planting_MD", "ETref", "ETc", "ETcadj", "E", "T", "DP", "Rain", "Irrig", "Veff_end")
df_filtered <- df_merged[, colnames(df_merged) %in% variables]

# Function to calculate summary statistics (Mean ± SD)
summary_stats <- function(data, group_col) {
  data %>%
    group_by(across(all_of(group_col))) %>%  # Group by selected column (e.g., Planting_MD)
    summarise(across(where(is.numeric), 
                     list(mean = ~ mean(.x, na.rm = TRUE), 
                          sd = ~ sd(.x, na.rm = TRUE)), 
                     .names = "{.col}_{.fn}"), 
              .groups = "drop")  # Drop grouping after summarization
}

# Compute summary stats for Planting_MD
summary_table <- summary_stats(df_filtered, "Planting_MD")

# Save to CSV
write.csv(summary_table, "Wheat_summary_mean_sd.csv", row.names = FALSE)

# Print output
print(summary_table)

# Save to CSV
write.csv(summary_table, "summary_mean_sd.csv", row.names = FALSE)

pd_plot <- ggplot(df_long, aes(x = Variable, y = Value, fill=Planting_MD, group = interaction(Variable, Planting_MD))) +
  geom_boxplot(outlier.shape = 1) +
  labs(title = "Comparison of Wheat SWB by Dekad",
       x = "Variable",
       y = "mm",
       fill = "Planting_MD") +
  scale_fill_brewer(palette = "Set1") +  # Choose a ColorBrewer palette
  theme_bw() +
  theme(legend.position = "top") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +  # Rotate axis labels for readability
  # theme(panel.grid.minor = element_line(color = "gray70"))+
  # theme(panel.grid = element_line(color = "gray"))+
  theme(plot.title = element_text(hjust = 0.5))

ggsave("Wheat_comparison_by_dekad.png", pd_plot, width = 3000, height = 1500, units = "px", dpi = 200)
