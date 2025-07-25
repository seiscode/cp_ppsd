# PPSD Batch Processing and Visualization Tool

This project is developed by [the_Seismic_Data_Processing_Group](#About_the_Seismic_Data_Processing_Group) serving as a Python-based tool for seismological data analysis. It is specifically designed for the batch processing and visualization of Probabilistic Power Spectral Density (PPSD). The tool is built upon the [ObsPy](https://github.com/obspy/obspy) library, supports flexible parameter configuration via TOML files, and provides professional four-in-one analysis plots.

## Main Features

- **PPSD Computation**: Batch processing of seismic data files, compute PPSD and save as NPZ format
- **Multiple Plot Types**: Support for standard PPSD plots, temporal evolution plots, spectrograms
- **Four-in-One Analysis Chart**: Professional PSD value analysis and visualization tool (`run_plot_psd.py`)
- **Flexible Configuration**: Parameter setting through TOML configuration files
- **Detailed Logging**: Complete processing record and error tracking
- **Modular Design**: Support for separated computation and plotting, convenient for batch processing
- **Chinese Support**: Complete Chinese font support and localized interface
- **Light Color Scheme**: Professional scientific visualization color schemes

## Core Tools

### 1. run_cp_ppsd.py - PPSD Computation and Standard Plotting
Main PPSD computation and standard visualization tool, supporting:
- Batch PPSD computation
- Standard PPSD plots, temporal evolution plots, spectrograms
- NPZ file generation and management
- Configuration file-driven flexible processing

### 2. run_plot_psd.py - Professional PSD Analysis Tool
Specialized PSD value analysis and visualization tool, providing:
- **Four-in-One Analysis Chart**: PPSD probability density distribution, PSD value scatter plot, time period PSD curve comparison, reserved extension position
- **Light Color Scheme**: Blues and viridis color schemes, suitable for scientific reports
- **Chinese Font Support**: Automatic detection and configuration of Chinese fonts
- **High-Quality Output**: 300 DPI, suitable for print quality

## Quick Start

### 1. Environment Setup

#### Method 1: Install with conda only (Recommended)

```bash
# Clone the project
git clone <repository_url>
cd cp_ppsd

# Option A: Create environment.yml file (optional, environment.yml is already provided)
# First create environment.yml file with the following content:
cat > environment.yml << EOF
name: seis
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.12
  - obspy>=1.4.1
  - matplotlib>=3.5.0
  - numpy>=1.21.0
  - scipy>=1.7.0
  - toml>=0.10.2
  - tqdm>=4.62.0
EOF

# Then create and activate environment
conda env create -f environment.yml
conda activate seis

# Option B: One command to create environment and install packages
conda create -n seis python=3.12 obspy matplotlib numpy scipy toml tqdm -c conda-forge -y
conda activate seis

# Option C: Step-by-step installation
conda create -n seis python=3.12 -y
conda activate seis
conda install -c conda-forge obspy matplotlib numpy scipy toml tqdm -y
```

#### Method 2: Mixed Installation (Better Compatibility)

```bash
# Create conda environment
conda create -n seis python=3.12 -y
conda activate seis

# Install dependencies with conda
conda install jinja2 pygments -c conda-forge -y

# Install remaining dependencies with pip
pip install -r requirements.txt

# Install project in development mode
pip install -e .
```

### 2. System Requirements

- **Python**: >= 3.12
- **Operating System**: Linux, Windows 10, Windows 11
- **Recommended Environment**: conda environment management
- **Chinese Fonts**: Automatic installation or manual Chinese font package installation

```bash
# Ubuntu/Debian Chinese font installation
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk
```

### 3. Data Preparation

Ensure you have the following data files:
- **Seismic Data Files**: MiniSEED format (.mseed, .msd, .seed)
- **Instrument Response Files**: StationXML format (.xml) or dataless SEED format (.dataless)

### 4. Configuration File Setup

#### Computation Configuration File (config.toml)
```toml
# PPSD Computation Configuration File - Computation Only
# Usage: python run_cp_ppsd.py config.toml
# This configuration file will always attempt to compute PPSD and save NPZ files.

# === 1. Global Operation Control ===
log_level = "DEBUG"                   # Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. Input Data and Output Paths ===
# mseed_pattern can be a glob pattern (like "./data/*.mseed") or a directory path (like "./data/").
# If it's a directory path, the script will recursively search for all miniseed files in that directory (slower execution efficiency).
mseed_pattern = "./data/"             # Seismic data file directory or glob pattern
inventory_path = "./input/BJ.dataless" # Instrument response file path
output_dir = "./output/npz"           # NPZ file output directory

# === 3. Output Generation Control (Implicit) ===
# NPZ files will always be created.
# output_npz_filename_pattern defines the naming rule for generated NPZ data files.
#   Time information (from MiniSEED data start time):
#     {year}, {month}, {day}, {hour}, {minute}, {second}, {julday}
#     {datetime} (e.g., YYYYMMDDHHMM format compact timestamp)
#   Station information: {network}, {station}, {location}, {channel}
#     Example: "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"
# If not set or empty, the script will use default naming rules.
output_npz_filename_pattern = "PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz"

# === 4. PPSD Core Computation Parameters ([args] section) ===
[args]
# --- Time Segmentation and Windows ---
ppsd_length = 3600                   # Time window length (seconds), standard 1 hour.
overlap = 0.5                        # Window overlap ratio, 50% overlap.

# --- Frequency/Period Domain Parameters ---
period_limits = [0.01, 1000.0]       # Period range for PPSD computation (seconds).
period_smoothing_width_octaves = 1.0 # Period smoothing width (octaves).
period_step_octaves = 0.125          # Period step size (1/8 octave).

# --- Amplitude Domain Parameters (Power Binning) ---
db_bins = [-200.0, -50.0, 0.25]      # dB binning: [minimum value, maximum value, step size].

# --- Data Quality and Selection ---
skip_on_gaps = false                 # Whether to skip windows with data gaps.
                                     # McNamara2004 merges gapped traces by zero-padding, which produces identifiable anomalous PSD lines in PPSD plots.
                                     # Setting to true will not zero-pad, may result in data segments shorter than ppsd_length not being used.
# special_handling = "None"          # Special instrument handling. Optional values: "ringlaser", "hydrophone", "None"(default), or comment out.
                                     # None(default): Standard seismometer processing (instrument correction + differentiation, convert velocity to acceleration)
                                     # "ringlaser": No instrument correction, only divide by sensitivity in metadata, no differentiation
                                     # "hydrophone": Instrument correction without differentiation (preserve original physical quantity)

# The following related parameters are used for script-level external event removal logic, applied before data is fed to PPSD object, not direct PPSD.__init__ parameters.
# time_of_weekday = [1, 2, 3, 4, 5]     # Days of week for analysis (1=Monday, 7=Sunday), weekdays. Used for pre-filtering Trace objects, not direct PPSD parameter.
# processing_time_window = ["2023-01-01T00:00:00", "2023-01-31T23:59:59"] # (Optional) Specify absolute time window for processing data [start time, end time], ISO 8601 format. Used for pre-filtering Trace, not direct PPSD parameter.
# daily_time_window = ["01:00:00", "05:00:00"] # (Optional) Specify daily time window for processing data [start time, end time], HH:MM:SS format. Used for pre-filtering Trace, not direct PPSD parameter.
# enable_external_stalta_filter = false # Whether to enable external STA/LTA event removal preprocessing.
# sta_length = 120                    # (External STA/LTA) Short-term average length (seconds).
# lta_length = 600                    # (External STA/LTA) Long-term average length (seconds).
# stalta_thresh_on = 2.5              # (External STA/LTA) Trigger threshold upper limit.
# stalta_thresh_off = 1.5             # (External STA/LTA) Trigger threshold lower limit.
```

#### Plotting Configuration File (config_plot.toml)
```toml
# PPSD Computation Configuration File - Plotting Only
# Usage: python run_cp_ppsd.py config_plot.toml
# This configuration file is used to load one or more PPSD data (.npz files) from a specified directory and perform plotting operations.
# NPZ files should already be generated through computation-type configuration files (such as config.toml).
# If there are no valid NPZ files in the specified directory, or the NPZ files themselves have problems, the script may report errors or skip during processing.
# Plotting will always be executed.

# === 1. Global Operation Control ===
log_level = "DEBUG"                   # Log level: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

# === 2. Input Data and Output Paths ===
# NPZ files must pre-exist and be valid, otherwise the script should report error and exit.
# input_npz_dir specifies the directory containing one or more pre-computed PPSD data (.npz) files.
# The script will attempt to process all .npz files in that directory.
# output_dir is used to store generated images, it's recommended to organize generated images for each NPZ file into subdirectories or use unique filenames.
input_npz_dir = "./output/npz/"       # Specify directory path containing NPZ files
inventory_path = "./input/BJ.XML"     # Instrument response file path (may be needed for metadata during plotting, such as station name)

# === 3. Output Generation Control (Implicit) ===
output_dir = "./output/plots/"        # Output directory (images saved here)
# Images will always be generated.
# output_filename_pattern defines the naming rule for generated image files.
# The following placeholders can be used:
#   Plot type (determined during plotting): {plot_type} (plot_type="standard", plot_type="temporal", plot_type="spectrogram")
#   Time information (usually from PPSD data start time or processing time):
#     {year}, {month}, {day}, {hour}, {minute}, {second}, {julday}
#     {datetime} (e.g., YYYYMMDDHHMM format compact timestamp)
#   Station information: {network}, {station}, {location}, {channel}
#     Example: "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png"
# If this parameter is not set or empty, the script will use default naming rules based on NPZ filename.
output_filename_pattern = "{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png"

# === 4. Plot-Specific Parameters ([args] section) ===
# The following parameters directly control the appearance and content when generating images from loaded PPSD objects.
[args]
# --- Basic Plot Control ---
plot_type = ["standard", "temporal", "spectrogram"] # Plot types: can be a single string like "standard", "temporal", "spectrogram", or a list containing these values

# --- NPZ File Merge Strategy ---
npz_merge_strategy = true             # NPZ file plotting merge strategy. Boolean value:
                                      # false: Generate separate plot for each NPZ file (default)
                                      # true: Merge multiple NPZ files of the same network, station, location, channel into one plot
                                      # Merge mode is suitable for time series data of the same channel, can show long-term noise evolution trends

# --- "standard" (PPSD.plot) Plot Specific Options ---
show_histogram = true                 # (standard) Whether to draw the 2D histogram itself.
show_percentiles = false              # (standard) Whether to show approximate percentile lines.
percentiles = [0, 25, 50, 75, 100]   # (standard) If show_percentiles=true, specify percentiles to display.
show_mode = false                     # (standard) Whether to show mode PSD curve.
show_mean = false                     # (standard) Whether to show mean PSD curve.
show_noise_models = true              # (standard) Whether to show global noise models.
standard_grid = true                  # (standard) Whether to show grid on histogram.
period_lim = [0.01, 1000.0]           # (standard) Period range for PPSD standard plot display (seconds). If xaxis_frequency=true, this should be frequency (Hz).
xaxis_frequency = false               # (standard) Whether PPSD standard plot X-axis shows frequency (Hz) instead of period (seconds).
cumulative_plot = false               # (standard) Whether to show cumulative histogram (cumulative parameter in PPSD.plot).
show_coverage = true                  # (standard) Whether to show data coverage.
cumulative_number_of_colors = 20      # (standard) Number of discrete colors for cumulative histogram.

standard_cmap = "viridis"             # (standard) Color map scheme for PPSD plot. E.g., "viridis", "plasma", "inferno".

# --- "spectrogram" (PPSD.plot_spectrogram) Plot Specific Options ---
clim = [-180, -100]                   # (spectrogram) Amplitude limits for color map [min_db, max_db].
time_format_x_spectrogram = "%Y-%m-%d" # (spectrogram) Time format for Y-axis (time axis) tick labels.
spectrogram_grid = true               # (spectrogram) Whether to show grid on histogram.
spectrogram_cmap = "viridis"          # (spectrogram) Color map scheme for PPSD plot. E.g., "viridis", "plasma", "obspy_sequential", "pqlx".

# --- "temporal" (PPSD.plot_temporal) Plot Specific Options ---
temporal_plot_periods = [1.0, 8.0, 20.0] # (temporal) Specific periods (seconds) for plotting PSD value evolution curves over time.
time_format_x_temporal = "%H:%M"      # (temporal) Time format for X-axis (time axis) tick labels.
temporal_grid = true                  # (temporal) Whether to show grid on histogram.
temporal_cmap = "viridis"             # (temporal) Color map scheme for PPSD plot. E.g., "viridis", "plasma", "obspy_sequential", "pqlx".
```

### 5. Running the Program

#### Basic PPSD Computation and Plotting
```bash
# PPSD computation only
python run_cp_ppsd.py input/config.toml

# Plotting only (requires pre-computed NPZ files)
python run_cp_ppsd.py input/config_plot.toml

# Computation + Plotting
python run_cp_ppsd.py input/config.toml input/config_plot.toml
```

#### Professional PSD Analysis
```bash
# Generate four-in-one analysis chart using default NPZ files
python run_plot_psd.py

# Specify NPZ file
python run_plot_psd.py ./output/npz/PPSD_202503251600_BJ-DAX-00-BHZ.npz

# Specify NPZ file and output directory
python run_plot_psd.py ./output/npz/PPSD_data.npz ./custom_output/

# Run in conda environment
conda run -n seis python run_plot_psd.py
```

## Output Files Explanation

### NPZ Files (PPSD Data)
- **Location**: `./output/npz/`
- **Naming**: `PPSD_{datetime}_{network}-{station}-{location}-{channel}.npz`
- **Content**: PPSD probability density matrix, frequency axis, time information, computation parameters
- **Usage**: Data storage, subsequent analysis, custom plotting

### Standard PPSD Images
- **Location**: `./output/plots/`
- **Types**: standard, temporal, spectrogram
- **Format**: PNG, 300 DPI
- **Naming**: `{plot_type}_{datetime}_{network}-{station}-{location}-{channel}.png`

### Four-in-One Analysis Chart
- **Location**: User-specified directory (default `./output/plots/`)
- **Naming**: `psd_analysis_{datetime}_{network}-{station}-{location}-{channel}.png`
- **Content**: 
  - PPSD probability density distribution plot (Blues color scheme)
  - PSD value scatter plot (Blues color scheme)
  - PSD curve comparison for different time periods (viridis color scheme)
  - Reserved extension position
- **Features**: 16×12 inches, 300 DPI, Chinese font support

## Configuration File Details

### Important Parameter Explanations

#### Time Information Source
- **Filename Time**: From MiniSEED data start time, not processing time
- **Ensure Accuracy**: Filename can accurately reflect the actual time range of data

#### special_handling Parameter
- **"None"**: Standard seismometer processing (default)
- **"ringlaser"**: Ring laser gyroscope, only divide by sensitivity
- **"hydrophone"**: Hydrophone, instrument correction without differentiation

#### skip_on_gaps Parameter
- **false**: Zero-pad merge gapped data (McNamara2004 method)
- **true**: Skip windows with data gaps, ensure data purity

#### npz_merge_strategy Parameter
- **false**: Generate separate images for each NPZ file (default)
- **true**: Merge multiple NPZ files of the same channel into one plot

## Project Structure

```
cp_ppsd/
├── run_cp_ppsd.py           # Main PPSD computation tool
├── run_plot_psd.py          # Professional PSD analysis tool
├── cp_ppsd/                 # Core module directory
│   ├── __init__.py          # Module initialization file
│   ├── cp_psd.py            # PPSD processing core code
│   └── plot_psd_values.py   # PSD analysis visualization module
├── tests/                   # Test program directory
│   ├── README.md            # Test program documentation
│   ├── test_basic.py        # Basic functionality tests
│   ├── test_config_params.py # Configuration parameter tests
│   ├── test_special_handling*.py # Special instrument handling tests
│   ├── test_summary_report.py # Summary report tests
│   ├── analyze_npz_content.py # NPZ file content analysis tool
│   ├── ppsd_binning_demo.py # PPSD binning demonstration program
│   ├── config_optimization_report.py # Configuration optimization report generator
│   └── check_data_info.py   # Data information checking tool
├── input/                   # Input file directory
│   ├── config.toml          # Computation configuration file
│   ├── config_plot.toml     # Plotting configuration file
│   └── BJ.dataless         # Instrument response file
├── data/                    # Seismic data directory
│   └── *.mseed             # MiniSEED data files
├── output/                  # Output file directory
│   ├── npz/                # NPZ file storage directory
│   └── plots/              # Image file storage directory
├── logs/                    # Log file directory
├── setup.py                # Package installation script
├── requirements.txt        # Python dependency packages
├── README.md              # Project documentation
├── README_plot_psd.md     # PSD analysis tool documentation
└──  ...
```

## Application Scenarios

### 1. Station Noise Assessment
- Evaluate background noise levels of seismic stations
- Compare with Peterson noise models (NLNM/NHNM)
- Station site selection and performance evaluation

### 2. Noise Source Identification
- Identify natural noise sources (ocean microseisms, wind noise)
- Detect anthropogenic noise sources (traffic, industrial, power interference)
- Environmental impact assessment

### 3. Instrument Performance Diagnosis
- Detect seismometer performance issues
- Identify mechanical resonance and electronic noise
- Equipment maintenance and fault diagnosis

### 4. Long-term Monitoring Analysis
- Monitor long-term trends in station noise changes
- Seasonal variations and environmental impact analysis
- Station management and preventive maintenance

## Troubleshooting

### Common Issues

1. **Data Files Not Found**
   - Check if `mseed_pattern` path is correct
   - Confirm if file extensions are supported (.mseed, .msd, .seed)

2. **Instrument Response Errors**
   - Verify if `inventory_path` file exists
   - Confirm response file matches data SEED ID
   - Support StationXML (.xml) and dataless SEED (.dataless) formats

3. **Chinese Font Display Issues**
   ```bash
   # Install Chinese fonts
   sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk
   
   # Clear matplotlib font cache
   rm -rf ~/.cache/matplotlib
   ```

4. **Memory Insufficient**
   - Reduce `ppsd_length` parameter
   - Adjust `db_bins` range and step size
   - Process data in batches

5. **NPZ File Loading Failed**
   - Check if file path is correct
   - Verify if NPZ file was generated by correct PPSD program
   - Confirm file permissions are readable

### Performance Optimization

#### Memory Optimization
```toml
[args]
ppsd_length = 1800          # Reduce window length
period_step_octaves = 0.25  # Increase period step size
db_bins = [-180, -80, 0.5]  # Reduce dB binning range
```

#### Computation Speed Optimization
```toml
[args]
skip_on_gaps = true         # Skip windows with data gaps
overlap = 0.25              # Reduce window overlap ratio
period_limits = [0.1, 100]  # Limit period range
```

### Log Analysis

Setting `log_level = "DEBUG"` can provide detailed processing information:
- File loading process
- PPSD computation progress
- Detailed error information
- Performance statistics

## Best Practices

### 1. Data Preparation
- Ensure accurate synchronization of data timestamps
- Verify validity of instrument response files
- Check data quality and completeness

### 2. Parameter Selection
- Choose appropriate time window length based on analysis objectives
- Balance frequency resolution and statistical stability
- Consider data quality when adjusting skip_on_gaps parameter

### 3. Result Validation
- Compare with known noise models
- Cross-validate results from different time periods
- Verify computational accuracy through independent methods

### 4. Quality Control
- Regular monitoring of processing logs
- Systematic validation of output files
- Documentation of analysis parameters and procedures

## Technical Support

For technical questions and support:
1. Check project documentation and FAQ
2. Review log files for error diagnosis  
3. Validate configuration parameters
4. Test with sample data sets

## About the Seismic Data Processing Group

Our group focuses on cutting-edge research and software development in the field of seismology. The team is led by Lin Xiangdong, with core members including Mu Leiyu, Yang Xuan, and Wu Peng.

Our key objectives include:

- Algorithm Development: Building on the theoretical foundations of the book Seismic Data Processing Techniques¹, we are dedicated to developing advanced seismological algorithms. These algorithms serve as both extensions and supplements to the classic methods in the book, while also incorporating our team's innovative approaches to enhance the precision and efficiency of data processing.
- Open-Source Contributions: Providing stable and efficient open-source programs for seismic data processing to serve the scientific community.
- Data Research: Conducting analysis of real-world seismic data and publishing our findings in academic papers.

We are committed to bridging the gap between theoretical research and practical application to drive progress in the field of seismology.

## License

This project follows open source license terms. Please refer to the LICENSE file for detailed information.

## Contributing

We welcome contributions to improve this project:
1. Submit bug reports and feature requests
2. Contribute code improvements and optimizations
3. Improve documentation and examples
4. Share analysis results and best practices

## Version History

See CHANGELOG.md for detailed version update information.

---

**Note**: This tool is designed for seismological research and professional applications. Users should have appropriate background knowledge in seismology and signal processing. 
