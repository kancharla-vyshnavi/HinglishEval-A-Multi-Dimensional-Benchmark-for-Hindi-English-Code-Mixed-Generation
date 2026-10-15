import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

df_h = pd.read_csv('research_upgrade/tables/human_ratings_annotator_a_500.csv')
df_m = pd.read_csv('outputs/independent_judge_1000/independent_mistral_judge__FINAL.csv')

print('Human rows:', len(df_h))
print('Mistral rows:', len(df_m))

merged = pd.merge(df_h, df_m, on=['row_index', 'model'], suffixes=('_human', '_mistral'))
print('Merged matches on (row_index, model):', len(merged))

dims = ['fluency', 'code_mixing_naturalness', 'hindi_grammar', 'prompt_adherence', 'spelling_consistency', 'overall']
for d in dims:
    vh = merged[f'{d}_human'].values
    vm = merged[f'{d}_mistral'].values
    rho, p_rho = stats.spearmanr(vh, vm)
    tau, p_tau = stats.kendalltau(vh, vm)
    qwk = cohen_kappa_score(vh, vm.round().astype(int), weights='quadratic')
    diff = vm.mean() - vh.mean()
    print(f"{d:25s} | Human={vh.mean():.3f} | Mistral={vm.mean():.3f} | Diff={diff:+.3f} | Spearman={rho:.4f} | Kendall={tau:.4f} | QWK={qwk:.4f}")
