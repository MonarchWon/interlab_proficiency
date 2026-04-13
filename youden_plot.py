import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from adjustText import adjust_text

def get_robust_cov(x, y):
    median_x = np.median(x)
    median_y = np.median(y)
    
    mad_x = np.median(np.abs(x - median_x))
    mad_y = np.median(np.abs(y - median_y))
    s_x = 1.4826 * mad_x
    s_y = 1.4826 * mad_y
    var_x = s_x ** 2 if s_x > 0 else 1e-6
    var_y = s_y ** 2 if s_y > 0 else 1e-6
    
    u = x + y
    v = x - y
    mad_u = np.median(np.abs(u - np.median(u)))
    mad_v = np.median(np.abs(v - np.median(v)))
    s_u = 1.4826 * mad_u
    s_v = 1.4826 * mad_v
    
    var_u = s_u ** 2
    var_v = s_v ** 2
    cov_xy = (var_u - var_v) / 4.0
    
    return np.array([[var_x, cov_xy], [cov_xy, var_y]]), median_x, median_y

def draw_confidence_ellipse(x, y, ax, n_std=2.4477, use_robust=True, **kwargs):
    if x.size != y.size:
        raise ValueError("x and y must be the same size")
        
    if np.var(x) == 0 or np.var(y) == 0:
        return None

    if use_robust:
        cov, mean_x, mean_y = get_robust_cov(x, y)
    else:
        cov = np.cov(x, y)
        mean_x = np.mean(x)
        mean_y = np.mean(y)

    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    pearson = max(min(pearson, 1.0), -1.0) # Clamp for numerical stability

    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)

    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, **kwargs)

    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def plot_youden_from_data(x, y, labels, title, output_path, xlabel, ylabel):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#f4f4f5')
    ax.set_facecolor('#ffffff')
    
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    labels = np.array(labels, dtype=str)

    draw_confidence_ellipse(x, y, ax, facecolor='yellow', edgecolor='red', linestyle='solid', linewidth=1.5, alpha=0.2, label='95% Confidence Ellipse')

    ax.scatter(x, y, color='#f97316', alpha=0.9, edgecolors='#ea580c', s=40, label='Lab Results', zorder=5)
    
    median_x = np.median(x) if len(x) > 0 else 0
    median_y = np.median(y) if len(y) > 0 else 0
    
    ax.axvline(median_x, color='black', linestyle='-', linewidth=1.2, alpha=0.8, label=f'Median X', zorder=3)
    ax.axhline(median_y, color='black', linestyle='-', linewidth=1.2, alpha=0.8, label=f'Median Y', zorder=3)
    
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    
    line_x = np.linspace(min(x_min, y_min - median_y + median_x)-10, max(x_max, y_max - median_y + median_x)+10, 100)
    line_y = line_x - median_x + median_y
    ax.plot(line_x, line_y, color='black', linestyle='-', linewidth=1.2, alpha=0.8, label='45° Reference Line', zorder=2)
    
    if len(x) > 0:
        cov = np.cov(x, y) if len(x) > 1 else [[1,0],[0,1]]
        std_x_span = np.sqrt(cov[0, 0]) * 2.4477 if len(x) > 1 else 5
        std_y_span = np.sqrt(cov[1, 1]) * 2.4477 if len(y) > 1 else 5
        
        min_x = min(x.min(), np.mean(x) - std_x_span)
        max_x = max(x.max(), np.mean(x) + std_x_span)
        min_y = min(y.min(), np.mean(y) - std_y_span)
        max_y = max(y.max(), np.mean(y) + std_y_span)
        
        x_pad = (max_x - min_x) * 0.15 if max_x != min_x else 10
        y_pad = (max_y - min_y) * 0.15 if max_y != min_y else 10
        
        ax.set_xlim(min_x - x_pad, max_x + x_pad)
        ax.set_ylim(min_y - y_pad, max_y + y_pad)
    
    # Use adjustText to dynamically place labels avoiding overlap
    texts = []
    for i, txt in enumerate(labels):
        texts.append(ax.text(x[i], y[i], txt, fontsize=9, color='#3f3f46', zorder=6))
        
    adjust_text(texts, x=x, y=y, ax=ax, 
                arrowprops=dict(arrowstyle='-', color='#a1a1aa', lw=0.8),
                expand_points=(1.5, 1.5))
        
    ax.set_title(f'Youden Summary Plot - {title}', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    
    ax.grid(False)
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', frameon=True, edgecolor='#d4d4d8', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Saved plot: {output_path}")

def process_excel_files(data_folder="data", excluded_labs=[]):
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        
    excel_files = glob.glob(os.path.join(data_folder, "*.xlsx")) + glob.glob(os.path.join(data_folder, "*.xls"))
    
    if not excel_files:
        return False
        
    for file in excel_files:
        print(f"\nProcessing workbook: {os.path.basename(file)}")
        try:
            excel_data = pd.read_excel(file, sheet_name=None)
            for sheet_name, df in excel_data.items():
                if len(df.columns) < 3:
                    continue
                    
                df_clean = df.iloc[:, :3].dropna()
                
                # Exclude specific labs
                if excluded_labs:
                    # Filter out any lab IDs present in excluded_labs
                    mask = ~df_clean.iloc[:, 0].astype(str).isin(excluded_labs)
                    df_clean = df_clean[mask]
                
                if df_clean.empty:
                    print(f"  -> Skipping '{sheet_name}': No valid data or all excluded.")
                    continue
                
                print(f"  -> Generating plot for '{sheet_name}'...")
                
                # Fetch labels and dynamic column headers
                labels = df_clean.iloc[:, 0].astype(str).values
                xlabel = str(df.columns[1])
                ylabel = str(df.columns[2])
                
                try: 
                    x = pd.to_numeric(df_clean.iloc[:, 1]).values
                    y = pd.to_numeric(df_clean.iloc[:, 2]).values
                except ValueError as e:
                    print(f"  -> Error plotting '{sheet_name}': Non-numeric data found!")
                    continue
                
                safe_sheet = "".join([c if c.isalnum() else "_" for c in sheet_name])
                out_path = os.path.join(data_folder, f"youden_{safe_sheet}.png")
                
                plot_youden_from_data(x, y, labels, sheet_name, out_path, xlabel, ylabel)
        except Exception as e:
            print(f"Error processing '{file}': {e}")
    return True

if __name__ == "__main__":
    print("-" * 60)
    print("Welcome to Youden Plot Generator!")
    print("\n--- CONFIGURATION ---")
    
    # You can add LAB IDs to this list to automatically drop them before plotting
    # Example: LABS_TO_EXCLUDE = ["Lab24", "Lab10"]
    LABS_TO_EXCLUDE = [] 
    
    if len(LABS_TO_EXCLUDE) > 0:
        print(f"Excluding Labs: {', '.join(LABS_TO_EXCLUDE)}")
    print("-" * 60)
    
    found_files = process_excel_files(excluded_labs=LABS_TO_EXCLUDE)
    
    if not found_files:
        print("\nNo Excel files found in the 'data' folder.")
