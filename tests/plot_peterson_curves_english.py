#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peterson Curves Plotting Tool
Generate Peterson (1993) New Low/High Noise Models (NLNM/NHNM)
Standard reference curves for seismic station noise evaluation

Author: muly
Created: 2025-01-30
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def get_nlnm_data():
    """
    Get Peterson New Low Noise Model (NLNM) data points
    Peterson, J. (1993). Observations and modeling of seismic background noise. 
    US Geological Survey open-file report, 93-322.
    """
    # Period (seconds) and corresponding PSD (dB relative to 1 (m/s²)²/Hz)
    periods = np.array([
        0.10, 0.17, 0.40, 0.80, 1.24, 2.40, 4.30, 5.00, 6.00, 10.00,
        12.00, 15.60, 21.90, 31.60, 45.00, 70.00, 101.00, 154.00,
        328.00, 600.00, 10000.00
    ])
    
    # NLNM Power Spectral Density values
    power = np.array([
        -162.36, -166.7, -170.0, -166.4, -168.6, -159.98, -141.1, -71.36,
        -97.26, -132.18, -205.27, -37.65, -114.37, -160.58, -187.50,
        -216.47, -185.00, -168.34, -217.43, -258.28, -346.88
    ])
    
    return periods, power

def get_nhnm_data():
    """
    Get Peterson New High Noise Model (NHNM) data points
    """
    # Period (seconds) and corresponding PSD (dB relative to 1 (m/s²)²/Hz)
    periods = np.array([
        0.10, 0.22, 0.32, 0.80, 3.80, 4.60, 6.30, 7.90, 15.40, 20.00,
        354.80, 10000.00
    ])
    
    # NHNM Power Spectral Density values
    power = np.array([
        -108.73, -150.34, -122.31, -116.85, -108.48, -74.66, -93.95,
        -73.54, -81.77, -69.86, -93.30, -98.17
    ])
    
    return periods, power

def interpolate_model(periods, power, target_periods):
    """
    Interpolate Peterson model at target period points
    """
    # Logarithmic space interpolation
    log_periods = np.log10(periods)
    log_target = np.log10(target_periods)
    
    # Linear interpolation
    interpolated_power = np.interp(log_target, log_periods, power)
    
    return interpolated_power

def plot_peterson_curves_english(save_path=None, show_plot=True):
    """
    Plot Peterson curves in English
    
    Parameters:
    -----------
    save_path : str, optional
        Save path, if None then don't save
    show_plot : bool, default True
        Whether to display the plot
    """
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Get Peterson model data
    nlnm_periods, nlnm_power = get_nlnm_data()
    nhnm_periods, nhnm_power = get_nhnm_data()
    
    # Create dense period grid for smooth curves
    period_range = np.logspace(-1, 4, 1000)  # 0.1 to 10000 seconds
    
    # Interpolate for smooth curves
    nlnm_interp = interpolate_model(nlnm_periods, nlnm_power, period_range)
    nhnm_interp = interpolate_model(nhnm_periods, nhnm_power, period_range)
    
    # Plot Peterson curves
    ax.semilogx(period_range, nlnm_interp, 'b-', linewidth=2.5, 
                label='NLNM (New Low Noise Model)', alpha=0.8)
    ax.semilogx(period_range, nhnm_interp, 'r-', linewidth=2.5, 
                label='NHNM (New High Noise Model)', alpha=0.8)
    
    # Plot original data points
    ax.semilogx(nlnm_periods, nlnm_power, 'bo', markersize=4, alpha=0.7)
    ax.semilogx(nhnm_periods, nhnm_power, 'ro', markersize=4, alpha=0.7)
    
    # Fill area between NLNM and NHNM
    ax.fill_between(period_range, nlnm_interp, nhnm_interp, 
                   alpha=0.2, color='gray', label='Normal Noise Range')
    
    # Set axes
    ax.set_xlim(0.1, 1000)
    ax.set_ylim(-250, -50)
    ax.set_xlabel('Period (s)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Power Spectral Density [dB rel. 1 (m/s²)²/Hz]', fontsize=14, fontweight='bold')
    
    # Add grid
    ax.grid(True, which='major', alpha=0.6, linestyle='-', linewidth=0.8)
    ax.grid(True, which='minor', alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Set title
    ax.set_title('Peterson Seismic Station Noise Models (Peterson, 1993)\n'
                'New Low/High Noise Models for Seismic Station Evaluation', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add legend
    legend = ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('black')
    
    # Add frequency labels (top axis)
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xscale('log')
    
    # Set frequency ticks (f = 1/T)
    period_ticks = np.array([0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000])
    freq_ticks = 1.0 / period_ticks
    ax2.set_xticks(period_ticks)
    ax2.set_xticklabels([f'{f:.2g}' for f in freq_ticks])
    ax2.set_xlabel('Frequency (Hz)', fontsize=14, fontweight='bold')
    
    # Add important frequency band annotations
    annotations = [
        (0.15, -80, 'High-freq\nCultural Noise', 'right'),
        (0.5, -140, 'Ocean Wave\nNoise', 'center'),
        (7, -90, 'Secondary\nMicroseisms', 'center'),
        (15, -120, 'Primary\nMicroseisms', 'center'),
        (100, -200, 'Atmospheric\nNoise', 'left'),
    ]
    
    for period, power, text, align in annotations:
        ax.annotate(text, xy=(period, power), xytext=(10, 10), 
                   textcoords='offset points', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                   ha=align)
    
    # Add explanation text
    info_text = (
        "Peterson (1993) Noise Model:\n"
        "• NLNM: Global quietest stations noise floor\n"
        "• NHNM: Global noisiest stations noise ceiling\n"
        "• Normal station noise should be between curves\n"
        "• Used for seismic station performance evaluation"
    )
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Peterson curves saved to: {save_path}")
    
    # Show plot
    if show_plot:
        plt.show()
    
    return fig, ax

def main():
    """
    Main function: Generate Peterson curve plots
    """
    print("Generating Peterson noise model curves...")
    
    # Create output directory
    output_dir = Path("./Docs/pics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main Peterson curves (period domain)
    fig1, ax1 = plot_peterson_curves_english(
        save_path=output_dir / "peterson_curves_english.png",
        show_plot=True
    )
    
    print(f"\n✅ Peterson curves generated successfully!")
    print(f"📁 Save path: {output_dir.absolute()}")
    print(f"📊 Generated file: peterson_curves_english.png")

if __name__ == "__main__":
    main() 