# ------------------------------------------------------------------
# PART 2: ABM CALIBRATION TO HISTORICAL CASES
# ------------------------------------------------------------------

HISTORICAL_CASES = [
    {'name': 'Nazi Germany (1939)', 'g': 0.25, 'cap_ratio': 1.3, 'actual': 0},
    {'name': 'Imperial Japan (1941)', 'g': 0.28, 'cap_ratio': 0.4, 'actual': 0},
    {'name': 'North Korea (1950)', 'g': 0.22, 'cap_ratio': 0.3, 'actual': 0},
    {'name': 'Soviet Union (1979)', 'g': 0.35, 'cap_ratio': 3.0, 'actual': 0},
    {'name': 'Iraq (1990)', 'g': 0.20, 'cap_ratio': 2.5, 'actual': 0},
    {'name': 'United States (1965)', 'g': 0.72, 'cap_ratio': 4.0, 'actual': 0},
    {'name': 'Argentina (1982)', 'g': 0.30, 'cap_ratio': 0.8, 'actual': 0},
]

def simulate_single_war(g, cap_ratio, lambda_g=2.5, lambda_R=1.0, n_trials=1000):
    """
    Simulate a single war given initiator granularity and capability ratio.
    Returns mean win probability.
    """
    epsilon = np.random.normal(0, 0.5, n_trials)
    logit = lambda_g * g + lambda_R * np.log(cap_ratio) + epsilon
    wins = expit(logit)
    return wins.mean()

def calibrate_abm_to_cases():
    results = []
    for case in HISTORICAL_CASES:
        p_win = simulate_single_war(case['g'], case['cap_ratio'])
        predicted = 1 if p_win > 0.5 else 0
        results.append({
            'Case': case['name'],
            'g': case['g'],
            'cap_ratio': case['cap_ratio'],
            'P(win)': p_win,
            'Predicted': 'Win' if predicted == 1 else 'Defeat',
            'Actual': 'Win' if case['actual'] == 1 else 'Defeat',
            'Match': predicted == case['actual']
        })
    
    df_results = pd.DataFrame(results)
    print("\n=== ABM Calibration to Historical Cases ===")
    print(df_results.to_string(index=False))
    print(f"\nCalibration accuracy: {df_results['Match'].mean():.1%}")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#2ca02c' if r else '#d62728' for r in df_results['Match']]
    bars = ax.barh(df_results['Case'], df_results['P(win)'], color=colors, edgecolor='black')
    ax.axvline(0.5, color='black', linestyle='--', linewidth=1.5, label='Decision threshold')
    ax.set_xlabel('Predicted win probability')
    ax.set_title('ABM calibration: predicted vs. actual outcomes of historical wars')
    ax.set_xlim(0, 1)
    ax.legend()
    
    for bar, pred, actual in zip(bars, df_results['Predicted'], df_results['Actual']):
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{pred} (actual: {actual})', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'figure_calibration_cases.png'), 
                bbox_inches='tight')
    plt.close()
    
    return df_results
