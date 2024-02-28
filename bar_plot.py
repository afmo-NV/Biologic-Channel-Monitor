import matplotlib.pyplot as plt
import logging


def create_plot_channel_availability(df):
    """
    Create a bar plot of channel availability per day and availability category from a dataframe with the following
     columns: 'Day', 'Hour', 'Availability'
    :param df: Dataframe with the following columns: 'Day', 'Hour', 'Availability'
    :return: Figure object
    """
    # Log the creation of the bar plot
    logging.debug(f"Creating bar plot of channel availability per day and availability category")

    # Sort dataframe by hour
    df = df.sort_values(by='Hour')
    # Group by day and availability category
    grouped = df.groupby(['Day', 'Availability']).size().unstack(fill_value=0)

    # Plotting
    colors = ["#00966C", "#C0F1DD", "#336B59", "#67CDA7", "#1D4438"]
    fig, ax = plt.subplots()

    # Get unique availability categories
    availability_categories = df['Availability'].unique()
    num_categories = len(availability_categories)
    bar_width = 0.2

    # Plot each availability category for each day with different color
    for i, category in enumerate(availability_categories):
        day_positions = range(1, len(grouped.index) + 1)
        bar_positions = [x + i * bar_width - (num_categories - 1) * bar_width / 2 for x in day_positions]

        # Adjust the position for single bars per day
        if len(grouped.columns) == 1:
            bar_positions = [x for x in day_positions]

        bars = ax.bar(bar_positions, grouped[category], width=bar_width, align='center', label=category,
                      color=colors[i])

        # Add text annotations for non-zero values
        for bar, value in zip(bars, grouped[category]):
            if value != 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), value, ha='center', va='bottom',
                        fontsize=8)

    ax.set_xlabel('Day', fontname='Arial', fontsize=12)
    ax.set_ylabel('Number of Channels', fontname='Arial', fontsize=12)
    ax.set_title('Channel Availability Per Day', fontname='Arial', fontsize=14)

    # Set x-axis ticks to display only the day
    ax.set_xticks(range(1, len(grouped.index) + 1))
    ax.set_xticklabels(grouped.index)

    # Add legend for each availability category
    ax.legend(title='Availability', fontsize=10)

    # Log the creation of the bar plot
    logging.debug(f"Bar plot of channel availability per day and availability category created")

    return fig


def save_figure(fig,filename):
    """
    Save the figure to a file
    :param fig: Figure object
    :param filename: Filename including path to save the figure
    :return: None
    """
    # Log the saving of the figure
    logging.debug(f"Saving figure to {filename}")

    # Save figure
    plt.savefig(filename, dpi=300)
    plt.close(fig)

    # Log the saving of the figure
    logging.debug(f"Figure saved to {filename}")

    return None