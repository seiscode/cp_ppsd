#!/usr/bin/env python3
"""
BJ Network Station Response Plotting Tool (English Version)

Plot instrument response for BJ.BBS, BJ.DAX, BJ.DSQ, BJ.FHY, BJ.JIZ stations.
This version uses English labels to avoid Chinese font display issues.

Reference:
https://docs.obspy.org/master/packages/autogen/obspy.core.inventory.inventory.Inventory.plot_response.html
"""

import os
import matplotlib.pyplot as plt
from obspy import read_inventory
import matplotlib

# Set non-interactive backend
matplotlib.use('Agg')

# Configure English fonts
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['figure.titlesize'] = 16


def plot_station_response_english(inventory, station, output_dir):
    """
    Plot individual station response with English labels
    """
    try:
        station_inv = inventory.select(station=station)
        if len(station_inv.networks) == 0:
            print(f"  Warning: Station {station} not found in inventory")
            return False
            
        # Display station channel info
        print(f"  Station {station} channels:")
        for network in station_inv.networks:
            for sta in network.stations:
                for chan in sta.channels:
                    print(f"    {network.code}.{sta.code}."
                          f"{chan.location_code}.{chan.code}")
        
        # Create figure
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # English title
        fig.suptitle(f'BJ.{station} Station Instrument Response', 
                     fontsize=16, fontweight='bold')
        
        # Plot response
        inventory.plot_response(
            min_freq=0.001,  # 0.001 Hz (1000s period)
            output='VEL',    # Velocity response
            network='BJ',
            station=station,
            location='*',
            channel='*',
            axes=axes,
            show=False,
            label_epoch_dates=True
        )
        
        # Set English axis labels and titles
        axes[0].set_title(f'Amplitude Response - Station {station}')
        axes[1].set_title(f'Phase Response - Station {station}')
        axes[0].set_ylabel('Amplitude (dB)')
        axes[1].set_ylabel('Phase (degrees)')
        axes[1].set_xlabel('Frequency (Hz)')
        
        # Add grid
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save image
        output_file = os.path.join(output_dir, f"BJ_{station}_response_en.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"  Response plot saved: {output_file}")
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"  Error plotting station {station}: {e}")
        return False


def plot_comparison_response_english(inventory, stations, output_dir):
    """
    Plot multi-station comparison response (English version)
    """
    try:
        # Create comparison figure
        fig, axes = plt.subplots(2, 1, figsize=(16, 12))
        
        # English title
        station_names = ', '.join(stations)
        fig.suptitle(f'BJ Network Multi-Station Response Comparison ({station_names})', 
                     fontsize=16, fontweight='bold')
        
        valid_stations = []
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, station in enumerate(stations):
            try:
                station_inv = inventory.select(station=station)
                if len(station_inv.networks) > 0:
                    # Plot vertical component response
                    inventory.plot_response(
                        min_freq=0.001,
                        output='VEL',
                        network='BJ',
                        station=station,
                        location='*',
                        channel='*Z',  # Only vertical component
                        axes=axes,
                        show=False,
                        label_epoch_dates=False
                    )
                    valid_stations.append(station)
                    print(f"  Added station {station} to comparison plot")
                    
            except Exception as e:
                print(f"  Warning: Station {station} cannot be added: {e}")
                continue
        
        # Set English titles and labels
        axes[0].set_title('Amplitude Response Comparison (Vertical Components)', 
                         fontsize=14)
        axes[1].set_title('Phase Response Comparison (Vertical Components)', 
                         fontsize=14)
        axes[0].set_ylabel('Amplitude (dB)')
        axes[1].set_ylabel('Phase (degrees)')
        axes[1].set_xlabel('Frequency (Hz)')
        
        # Add grid
        axes[0].grid(True, alpha=0.3)
        axes[1].grid(True, alpha=0.3)
        
        # Adjust legend
        if valid_stations:
            axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # Save comparison plot
        comparison_file = os.path.join(output_dir, 
                                     "BJ_stations_response_comparison_english.png")
        plt.savefig(comparison_file, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print(f"  English comparison plot saved: {comparison_file}")
        
        plt.close(fig)
        
        return len(valid_stations)
        
    except Exception as e:
        print(f"  Error plotting English comparison: {e}")
        return 0


def main():
    """
    Main function - Plot specified station responses
    """
    print("=" * 70)
    print("BJ Network Station Response Plotting Tool (English Version)")
    print("Target stations: BBS, DAX, DSQ, FHY, JIZ")
    print("=" * 70)
    
    # Input file path
    inventory_file = "../input/BJ.XML"
    
    # Check file existence
    if not os.path.exists(inventory_file):
        print(f"Error: Cannot find inventory file {inventory_file}")
        return
    
    # Read inventory
    print(f"Reading inventory file: {inventory_file}")
    try:
        inventory = read_inventory(inventory_file)
        print(f"Successfully read inventory with {len(inventory.networks)} networks")
    except Exception as e:
        print(f"Error reading inventory file: {e}")
        return
    
    # Specify target stations
    target_stations = ['BBS', 'DAX', 'DSQ', 'FHY', 'JIZ']
    
    # Check which stations are available
    all_stations = []
    for network in inventory.networks:
        for station in network.stations:
            all_stations.append(station.code)
    
    available_stations = [s for s in target_stations if s in all_stations]
    missing_stations = [s for s in target_stations if s not in all_stations]
    
    print(f"\n=== Station Status Check ===")
    print(f"All stations in BJ.XML: {', '.join(sorted(all_stations))}")
    print(f"Target stations: {', '.join(target_stations)}")
    print(f"Available stations: {', '.join(available_stations)}")
    if missing_stations:
        print(f"Missing stations: {', '.join(missing_stations)}")
    
    # Create output directory
    output_dir = "../output/response_plots"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Plot individual station responses
    print(f"\n=== Plotting Individual Station Responses ===")
    successful_plots = 0
    
    for station in available_stations:
        print(f"\nProcessing station: {station}")
        if plot_station_response_english(inventory, station, output_dir):
            successful_plots += 1
    
    print(f"\nSuccessfully plotted {successful_plots} individual station responses")
    
    # Plot comparison chart
    if available_stations:
        print(f"\n=== Plotting Multi-Station Comparison ===")
        valid_count = plot_comparison_response_english(inventory, 
                                                     available_stations, 
                                                     output_dir)
        print(f"Comparison plot contains {valid_count} station responses")
    
    # Generate summary report
    print(f"\n=== Plotting Complete ===")
    print(f"Requested stations: {', '.join(target_stations)}")
    print(f"Successfully processed: {', '.join(available_stations)}")
    if missing_stations:
        print(f"Not found: {', '.join(missing_stations)}")
    print(f"Generated images: {successful_plots + (1 if available_stations else 0)}")
    print(f"All images saved in: {output_dir}")
    
    # List generated files
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) 
                if f.endswith('.png') and '_en' in f]
        if files:
            print(f"\nNew English version files generated:")
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  {file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main() 