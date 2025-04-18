library(dplyr)
library(ggplot2)
library(reshape2)

df_merged <- read.csv("./TPR_DSR_merged.csv")
df_merged$Planting_Date <- as.Date(df_merged$Planting_Date, format = "%Y-%m-%d")
df_merged$Planting_MD <- format(df_merged$Planting_Date, "%m-%d")

# Filter for the specific conditions
df_filtered <- df_merged %>%
  filter(
    (Planting_MD == "07-01" & Irrig_Crit == "0.75" & Season == 120 & Method == "DSR") |
    (Planting_MD == "07-01" & Irrig_Crit == "10" & Season == 120 & Method == "TPR")
  )

dsr_good <- df_merged %>%
  filter(Planting_MD == "07-01" & Irrig_Crit == "0.75" & Season == 120 & Method == "DSR")
dsr_current <- df_merged %>%
  filter(Planting_MD == "05-15" & Irrig_Crit == "0.47" & Season == 120 & Method == "DSR")

tpr_good <- df_merged %>%
  filter(Planting_MD == "07-01" & Irrig_Crit == "0.75" & Season == 120 & Method == "TPR")
tpr_current <- df_merged %>%
  filter(Planting_MD == "06-01" & Irrig_Crit == "10" & Season == 135 & Method == "TPR")

# Define the variables you want to summarize
variables <- c("ETref", "ETc", "ETcadj", "E", "T", "DP", "Rain", "Irrig", "Veff_end")

# Function to calculate mean ± SD
summary_stats <- function(data, label) {
  data %>%
    summarise(across(all_of(variables), 
                     list(mean = ~ mean(.x, na.rm = TRUE), 
                          sd = ~ sd(.x, na.rm = TRUE)), 
                     .names = "{.col}_{.fn}")) %>%
    mutate(Group = label)  # Add a label column
}

# Compute summary for each group
dsr_good_stats <- summary_stats(dsr_good, "DSR_Good")
dsr_current_stats <- summary_stats(dsr_current, "DSR_Current")
tpr_good_stats <- summary_stats(tpr_good, "TPR_Good")
tpr_current_stats <- summary_stats(tpr_current, "TPR_Current")

# Combine results into one table
summary_table <- bind_rows(dsr_good_stats, dsr_current_stats, tpr_good_stats, tpr_current_stats)

# Reorder columns: Group first
summary_table <- summary_table %>% select(Group, everything())

# Print the table
print(summary_table)

# Save to CSV
write.csv(summary_table, "summary_mean_sd.csv", row.names = FALSE)








# variables <- c("Planting_MD", "Irrig_Crit", "Method", "Season")
# variables <- c(variables, "ETref", "ETc", "E", "T", "DP", "Rain", "Irrig", "Veff_end")
# # variables <- c(variables, "ETref", "ETc")
# # variables <- c(variables, "E", "T")
# # variables <- c(variables, "DP", "Rain")
# # variables <- c(variables, "Irrig", "Veff_end")
# df_filtered <- df_filtered[, colnames(df_filtered) %in% variables]

# df_long <- melt(df_filtered, id.vars = c("Planting_MD", "Irrig_Crit", "Method" , "Season"), 
#                 variable.name = "Variable", 
#                 value.name = "Value")
# df_long$Irrig_Crit <- factor(df_long$Irrig_Crit, 
#                                        levels = c(10, 0.75), 
#                                        labels = c("TPR", "DSR"))

# # Create a boxplot comparing DSR vs TPR for a selected variable (e.g., ETc)
# pd_plot <- ggplot(df_long, aes(x = Variable, y = Value, fill=Irrig_Crit, group = interaction(Variable, Irrig_Crit))) +
#   geom_boxplot(outlier.shape = 1) +
#   ylim(0, 1300) +
#   labs(title = "Comparison of DSR-120d-15/05-20kPa vs TPR-135d-01/06-10mm",
#        x = "Variable",
#        y = "mm",
#        fill = "Method") +
#   scale_fill_brewer(palette = "Set1") +  # Choose a ColorBrewer palette
#   theme_bw() +
#   theme(legend.position = "top") +
#   theme(axis.text.x = element_text(angle = 90, hjust = 1)) +  # Rotate axis labels for readability
#   # theme(panel.grid.minor = element_line(color = "gray70"))+
#   # theme(panel.grid = element_line(color = "gray"))+
#   theme(plot.title = element_text(hjust = 0.5))

# ggsave("TPR_DSR_comparison_02.png", pd_plot, width = 10, height = 6, units = "in", dpi = 300)
