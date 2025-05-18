### Programmed by Claude 3.7 Sonnet
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
import seaborn as sns
from scipy import stats

# Set the style to match academic publications
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# Set color scheme similar to Foundations and Trends in ML
# Using a professional color palette
main_color = "#2f5c85"  # Deep blue
secondary_color = "#a63d40"  # Burgundy
accent_color = "#90323d"  # Dark red
light_color = "#d8e1e9"  # Light blue-gray
background_color = "#f8f9fa"  # Off-white

# The data (nDCG@20 scores)
data = pd.read_csv("dataset_ndcg_score.csv")["ndcg score"].tolist()

indices = np.arange(1, len(data) + 1)

# Calculate statistics
mean_value = np.mean(data)
median_value = np.median(data)
min_value = np.min(data)
max_value = np.max(data)
std_dev = np.std(data)
quartiles = np.percentile(data, [25, 75])

# Create figure with multiple subplots in academic style
fig = plt.figure(figsize=(10, 8), facecolor=background_color)
gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1], width_ratios=[3, 1])

# Main plot: Line and scatter plot
ax1 = plt.subplot(gs[0, 0])
ax1.plot(indices, data, color=main_color, linestyle='-', linewidth=1.5, alpha=0.7, zorder=1)
ax1.scatter(indices, data, color=main_color, s=50, edgecolor='white', linewidth=0.5, zorder=2)

# Add a horizontal line for the mean with explicit label
mean_label = f'Mean: {mean_value:.2f}%'
ax1.axhline(y=mean_value, color=secondary_color, linestyle='--', linewidth=1.2, 
           label=mean_label)

# Customize the main plot
ax1.set_xlim(0.5, len(data) + 0.5)
ax1.set_ylim(min_value - 5, max_value + 5)  # Increased range to fit annotations
ax1.set_xlabel('Query Index', fontweight='bold')
ax1.set_ylabel('nDCG@20 Score (%)', fontweight='bold')
ax1.xaxis.set_major_locator(MultipleLocator(2))
ax1.xaxis.set_minor_locator(MultipleLocator(1))
ax1.yaxis.set_major_locator(MultipleLocator(5))
ax1.yaxis.set_minor_locator(MultipleLocator(1))
# Ensure y-axis ticks are visible
y_ticks = np.arange(80, 101, 5)
ax1.set_yticks(y_ticks)
ax1.set_yticklabels([f'{y:.0f}' for y in y_ticks])
ax1.legend(frameon=True, framealpha=0.9, loc='lower right')

# Add value labels for each data point
for i, val in enumerate(data):
    ax1.text(i+1, val+0.7, f'{val:.1f}%', ha='center', va='bottom', 
             fontsize=7, rotation=45, color=main_color, alpha=0.8)

# Add annotations for min and max values
ax1.annotate(f'Min: {min_value:.2f}%', 
            xy=(np.argmin(data)+1, min_value),
            xytext=(np.argmin(data)+1, min_value-2.5),
            arrowprops=dict(facecolor=accent_color, shrink=0.05, width=1.5, headwidth=7),
            fontsize=9, ha='center', va='top', color=accent_color)

ax1.annotate(f'Max: {max_value:.2f}%', 
            xy=(np.argmax(data)+1, max_value),
            xytext=(np.argmax(data)+1, max_value+2.5),
            arrowprops=dict(facecolor=accent_color, shrink=0.05, width=1.5, headwidth=7),
            fontsize=9, ha='center', va='bottom', color=accent_color)

ax1.grid(True, linestyle='--', alpha=0.7)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Box plot on the right side
ax2 = plt.subplot(gs[0, 1], sharey=ax1)
boxplot = ax2.boxplot(data, vert=True, patch_artist=True, widths=0.6)
for patch in boxplot['boxes']:
    patch.set_facecolor(light_color)
    patch.set_edgecolor(main_color)
for whisker in boxplot['whiskers']:
    whisker.set_color(main_color)
    whisker.set_linestyle('-')
    whisker.set_linewidth(1.2)
for cap in boxplot['caps']:
    cap.set_color(main_color)
    cap.set_linewidth(1.2)
for median in boxplot['medians']:
    median.set_color(accent_color)
    median.set_linewidth(1.5)
for flier in boxplot['fliers']:
    flier.set_markerfacecolor(secondary_color)
    flier.set_markeredgecolor(secondary_color)
    flier.set_markersize(6)

ax2.set_title('Distribution', fontweight='bold')
ax2.set_xticks([])
# Keep y-axis ticks for the boxplot
ax2.yaxis.set_major_locator(MultipleLocator(5))
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Histogram at the bottom
ax3 = plt.subplot(gs[1, 0])
hist_bins = np.linspace(80, 100, 11)
ax3.hist(data, bins=hist_bins, color=light_color, edgecolor=main_color, 
         linewidth=1.2, alpha=0.8)
ax3.axvline(x=mean_value, color=secondary_color, linestyle='--', linewidth=1.2)

# Add KDE curve
density = stats.gaussian_kde(data)
x_range = np.linspace(min_value - 2, max_value + 2, 1000)
ax3.plot(x_range, density(x_range) * len(data) * (hist_bins[1] - hist_bins[0]), 
         color=accent_color, linewidth=1.5)

ax3.set_xlabel('nDCG@20 Score (%)', fontweight='bold')
ax3.set_ylabel('Frequency', fontweight='bold')
ax3.set_xlim(min_value - 3, max_value + 3)
ax3.xaxis.set_major_locator(MultipleLocator(5))
# Add x-axis ticks with explicit values
x_ticks = np.arange(80, 101, 5)
ax3.set_xticks(x_ticks)
ax3.set_xticklabels([f'{x:.0f}' for x in x_ticks])
ax3.grid(True, linestyle='--', alpha=0.7)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Statistics table
ax4 = plt.subplot(gs[1, 1])
ax4.axis('off')
stats_text = (
    f"Summary Statistics\n"
    f"───────────────────\n"
    f"n = {len(data)}\n"
    f"Mean = {mean_value:.2f}%\n"
    f"Median = {median_value:.2f}%\n"
    f"Min = {min_value:.2f}%\n"
    f"Max = {max_value:.2f}%\n"
    f"Std Dev = {std_dev:.2f}\n"
    f"Q1 = {quartiles[0]:.2f}%\n"
    f"Q3 = {quartiles[1]:.2f}%"
)
ax4.text(0.1, 0.5, stats_text, fontsize=10, va='center', family='monospace')

# Add a title with academic style
plt.suptitle('nDCG@20 Performance Analysis', fontsize=16, fontweight='bold', y=0.98)
plt.figtext(0.5, 0.93, 'Evaluation of Retrieval System Performance Across 20 Queries', 
            ha='center', fontsize=12, style='italic')

# Adjust layout and spacing
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.subplots_adjust(wspace=0.05, hspace=0.3)

# Save the figure in high resolution
plt.savefig('ndcg_performance.png', dpi=300, bbox_inches='tight', facecolor=background_color)
plt.savefig('ndcg_performance.pdf', format='pdf', bbox_inches='tight', facecolor=background_color)

# Display the plot
plt.show()