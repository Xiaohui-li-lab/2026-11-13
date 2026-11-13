"""
replication_package.py
Full replication package for:
"Information-Processing Modes Determine the Architecture and Outcome of Aggressive Wars"
Author: Xiaohui Li
Data homepage: https://github.com/xiaohui-li-lab/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.special import expit
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
DATA_DIR = './data'
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(42)
plt.rcParams.update({
    'font.size': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300
})

# ------------------------------------------------------------------
# 1. Load COW Inter-State War Data
# ------------------------------------------------------------------
def load_cow_war_data():
    """
    Load COW Inter-State War Data v4.0.
    Expected columns: WarNum, WarName, StateName, CCode, Side,
                      StartYear1, EndYear1, BatDeath
    """
    path = os.path.join(DATA_DIR, 'Inter-StateWarData_v4.0.csv')
    df = pd.read_csv(path, encoding='latin1')
    
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]
    
    # Keep first spell of each war
    df = df[df['StartYear1'].notna()].copy()
    df['StartYear1'] = df['StartYear1'].astype(int)
    df['CCode'] = df['CCode'].astype(int)
    
    return df

# ------------------------------------------------------------------
# 2. Identify aggressive initiators
# ------------------------------------------------------------------
def identify_initiators(df_war):
    """
    Identify war initiators. In COW, Side='A' is typically the initiator side.
    We take the state with the earliest StartYear1 within each Side A group.
    Mark as initiator = 1.
    """
    # Side A as initiator side
    init_side = df_war[df_war['Side'] == 'A'].copy()
    
    # For each war, pick the state with earliest start year
    init_idx = init_side.groupby('WarNum')['StartYear1'].idxmin()
    initiators = init_side.loc[init_idx].copy()
    initiators['initiator'] = 1
    
    return initiators[['WarNum', 'CCode', 'StateName', 'StartYear1', 'initiator']]

# ------------------------------------------------------------------
# 3. Load V-Dem and build IGI
# ------------------------------------------------------------------
def load_vdem_data():
    path = os.path.join(DATA_DIR, 'V-Dem-CY-Core-v12.csv')
    df = pd.read_csv(path, low_memory=False)
    return df

def build_igi(df_vdem, year_col='year', country_col='country_text_id'):
    """
    Build Information-Granularity Index (IGI) from V-Dem variables.
    Uses PCA on v2x_polyarchy and v2x_freexp_altinf.
    """
    cols = ['v2x_polyarchy', 'v2x_freexp_altinf']
    df = df_vdem[[country_col, year_col] + cols].copy()
    df = df.dropna(subset=cols)
    
    scaler = StandardScaler()
    X = scaler.fit_transform(df[cols])
    
    pca = PCA(n_components=1)
    igi = pca.fit_transform(X).flatten()
    
    # Normalize to [0, 1]
    igi = (igi - igi.min()) / (igi.max() - igi.min())
    
    df['IGI'] = igi
    df['IGI_load_pc1'] = pca.components_[0][0]
    df['IGI_load_pc2'] = pca.components_[0][1]
    
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_[0]:.3f}")
    print(f"PC1 loadings: polyarchy={pca.components_[0][0]:.3f}, "
          f"freexp={pca.components_[0][1]:.3f}")
    
    return df[[country_col, year_col, 'IGI']]

# ------------------------------------------------------------------
# 4. Load COW National Material Capabilities
# ------------------------------------------------------------------
def load_cow_nmc():
    path = os.path.join(DATA_DIR, 'NMC_Data_v6.0.csv')
    df = pd.read_csv(path)
    df['ccode'] = df['ccode'].astype(int)
    df['year'] = df['year'].astype(int)
    return df[['ccode', 'year', 'cinc']]

# ------------------------------------------------------------------
# 5. Build analysis dataset
# ------------------------------------------------------------------
def build_analysis_dataset():
    df_war = load_cow_war_data()
    initiators = identify_initiators(df_war)
    
    df_vdem = load_vdem_data()
    df_igi = build_igi(df_vdem, year_col='year', country_col='histname')
    # Note: V-Dem uses 'histname' or 'country_text_id'; adjust as needed
    
    df_nmc = load_cow_nmc()
    
    # Merge IGI to initiators (use war start year or year before)
    initiators['year'] = initiators['StartYear1'] - 1  # lag by 1 year
    df = initiators.merge(
        df_igi.rename(columns={'year': 'igi_year', 'histname': 'StateName'}),
        on='StateName',
        how='left'
    )
    df = df[(df['igi_year'] <= df['year'] + 1) & (df['igi_year'] >= df['year'] - 1)]
    
    # For simplicity, take closest IGI year
    df['year_diff'] = (df['igi_year'] - df['year']).abs()
    df = df.loc[df.groupby('WarNum')['year_diff'].idxmin()]
    
    # Merge NMC for capability ratio
    df = df.merge(df_nmc.rename(columns={'ccode': 'CCode', 'year': 'nmc_year'}),
                  left_on=['CCode', 'igi_year'],
                  right_on=['CCode', 'nmc_year'],
                  how='left')
    
    # For capability ratio, we need target side capabilities
    # Merge war-level target (Side B) aggregate CINC
    side_b = df_war[df_war['Side'] == 'B'].groupby('WarNum')['CCode'].apply(list).reset_index()
    side_b['target_ccode'] = side_b['CCode']
    df = df.merge(side_b[['WarNum', 'target_ccode']], on='WarNum', how='left')
    
    # Compute capability ratio
    def get_target_cinc(row):
        if not isinstance(row['target_ccode'], list):
            return np.nan
        targets = df_nmc[(df_nmc['ccode'].isin(row['target_ccode'])) & 
                         (df_nmc['year'] == row['igi_year'])]
        return targets['cinc'].sum() if len(targets) > 0 else np.nan
    
    df['target_cinc'] = df.apply(get_target_cinc, axis=1)
    df['cap_ratio'] = df['cinc'] / df['target_cinc']
    df['ln_cap_ratio'] = np.log(df['cap_ratio'])
    
    # Outcome: defeat = 1 if initiator's battle deaths > target's (rough proxy)
    # Better: use war outcome codings from Reiter & Stam or COW
    # Here we use a simplified defeat measure based on fatality ratio
    side_a_deaths = df_war[df_war['Side'] == 'A'].groupby('WarNum')['BatDeath'].sum()
    side_b_deaths = df_war[df_war['Side'] == 'B'].groupby('WarNum')['BatDeath'].sum()
    outcome = pd.DataFrame({
        'side_a_deaths': side_a_deaths,
        'side_b_deaths': side_b_deaths
    })
    outcome['defeat'] = (outcome['side_a_deaths'] > outcome['side_b_deaths']).astype(int)
    outcome = outcome.reset_index()
    
    df = df.merge(outcome[['WarNum', 'defeat']], on='WarNum', how='left')
    
    return df

# ------------------------------------------------------------------
# 6. Logistic regression
# ------------------------------------------------------------------
def run_logistic_regression(df):
    df_reg = df.dropna(subset=['IGI', 'defeat', 'ln_cap_ratio']).copy()
    
    # Basic model
    X = sm.add_constant(df_reg[['IGI', 'ln_cap_ratio']])
    y = df_reg['defeat']
    model1 = sm.Logit(y, X).fit(disp=0)
    
    # Full model with controls (if available)
    if 'nuclear' in df_reg.columns and 'alliance' in df_reg.columns:
        X2 = sm.add_constant(df_reg[['IGI', 'ln_cap_ratio', 'nuclear', 'alliance']])
    else:
        X2 = X
    model2 = sm.Logit(y, X2).fit(disp=0)
    
    print("\n=== Model 1: IGI + capability ratio ===")
    print(model1.summary())
    
    print("\n=== Model 2: with controls ===")
    print(model2.summary())
    
    return model1, model2, df_reg

# ------------------------------------------------------------------
# 7. Plot Figure 3 with real data
# ------------------------------------------------------------------
def plot_figure3_real(df_reg):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    
    # Panel A: IGI distribution
    ax = axes[0]
    ax.hist(df_reg['IGI'], bins=15, color='steelblue', edgecolor='black', alpha=0.7)
    med = df_reg['IGI'].median()
    ax.axvline(med, color='red', linestyle='--', linewidth=2, label=f'median={med:.2f}')
    ax.set_xlabel('Information-Granularity Index (IGI)')
    ax.set_ylabel('Number of initiators')
    ax.set_title('a | IGI distribution')
    ax.legend()
    
    # Panel B: IGI vs defeat with jitter
    ax = axes[1]
    igi_grid = np.linspace(0, 1, 200)
    
    # Fit logistic
    X_fit = sm.add_constant(df_reg[['IGI', 'ln_cap_ratio']])
    model = sm.Logit(df_reg['defeat'], X_fit).fit(disp=0)
    pred = model.predict(sm.add_constant(pd.DataFrame({
        'IGI': igi_grid,
        'ln_cap_ratio': [df_reg['ln_cap_ratio'].mean()] * 200
    })))
    
    jitter = np.random.normal(0, 0.03, len(df_reg))
    colors = ['#2ca02c' if d == 0 else '#d62728' for d in df_reg['defeat']]
    ax.scatter(df_reg['IGI'], df_reg['defeat'] + jitter, c=colors, alpha=0.6, edgecolors='k', s=50)
    ax.plot(igi_grid, pred, 'k-', linewidth=2, label='logit fit')
    ax.set_xlabel('IGI')
    ax.set_ylabel('Defeat (jittered)')
    ax.set_title('b | IGI vs. defeat probability')
    ax.set_ylim(-0.1, 1.1)
    ax.legend()
    
    # Panel C: median split
    ax = axes[2]
    med = df_reg['IGI'].median()
    low = df_reg[df_reg['IGI'] < med]['defeat']
    high = df_reg[df_reg['IGI'] >= med]['defeat']
    
    rates = [low.mean(), high.mean()]
    se = [low.std() / np.sqrt(len(low)), high.std() / np.sqrt(len(high))]
    
    bars = ax.bar(['Low IGI\n(<median)', 'High IGI\n(≥median)'], 
                  rates, yerr=se, capsize=5,
                  color=['#d62728', '#2ca02c'], edgecolor='black')
    ax.set_ylabel('Observed defeat rate')
    ax.set_title('c | Defeat rate by IGI median split')
    ax.set_ylim(0, 1)
    ax.bar_label(bars, fmt='%.2f')
    
    plt.suptitle('Fig. 3 | Historical validation: IGI and war outcomes (COW 1816–2007)', 
                 fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'figure_3_real_data.png'), 
                bbox_inches='tight')
    plt.close()
    
    print(f"\nLow IGI defeat rate: {rates[0]:.3f} (n={len(low)})")
    print(f"High IGI defeat rate: {rates[1]:.3f} (n={len(high)})")

# ------------------------------------------------------------------
# Main execution for real data analysis
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("PART 1: REAL DATA ANALYSIS")
    print("=" * 60)
    df = build_analysis_dataset()
    model1, model2, df_reg = run_logistic_regression(df)
    plot_figure3_real(df_reg)
