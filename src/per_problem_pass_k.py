import yaml
from pathlib import Path
import numpy as np
from all_prepare_prompts import TEMPS, LANGS, MODELS, VARIATION

def estimator(n: int, c: int, k: int) -> float:
    """
    Calculates 1 - comb(n - c, k) / comb(n, k).
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def per_problem_pass_k(dir, lang, model, temp, variation,pdict):
    for result_path in dir.glob("*.results.yaml"):
        try:
            with open (result_path) as f:
                results_yaml = yaml.safe_load(f)
            problem = result_path.name.split(".")[0]
            n_results = len(results_yaml["results"])
            n_ok_results = len([c for c in results_yaml["results"] if c["status"] == "OK"])
            if (temp == "0.2"):
                p1 = estimator(n_results, n_ok_results, 1)
                if problem in pdict:
                    pdict[problem]['pass_k1'] = p1
                else:
                    pdict[problem] = {'pass_k1':p1}
            else:
                pass_k10 = estimator(n_results, n_ok_results, 10)
                pass_k100 = estimator(n_results, n_ok_results, 100)
                #print(f"{problem},{lang},{model},{temp},{variation},1,{pass_k10}")
                #print(f"{problem},{lang},{model},{temp},{variation},1,{pass_k100}")
                if problem in pdict:
                    pdict[problem]['pass_k10'] = pass_k10
                    pdict[problem]['pass_k100'] = pass_k100
                else:
                    pdict[problem] = {'pass_k10':pass_k10,'pass_k100':pass_k100}
        except yaml.YAMLError as exc:
            continue
    return pdict


if __name__ == "__main__":
    print("lang,problem,model,temp,variation,pass@1,pass@10,pass@100")
    for lang in LANGS:
        for model in MODELS:
            for variation in VARIATION:
                pdict = {}
                for temp in TEMPS:
                    dir = Path(f"../experiments/{lang}-{model}-{temp}-{variation}")
                    if dir.exists():
                        pdict = per_problem_pass_k(dir,lang,model,temp,variation,pdict)
                for problem in pdict:
                    p1 = pdict[problem]['pass_k1'] if 'pass_k1' in pdict[problem] else 'NA'
                    p10 = pdict[problem]['pass_k10'] if 'pass_k10' in pdict[problem] else 'NA'
                    p100 = pdict[problem]['pass_k100'] if 'pass_k100' in pdict[problem] else 'NA'
                    print(f"{lang},{problem},{model},{variation},{p1},{p10},{p100}")