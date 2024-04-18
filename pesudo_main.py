import os
from flaml import oai
from math_chat import MathChat
import argparse
from utils import mylogger, load_level5_math_test_each_category, load_fixed, random_sample_MATH


def parse_args():
    parser = argparse.ArgumentParser(description="Math mathchat_solver")
    parser.add_argument("--prompt_type", "-ptype", dest="prompt_type", help="prompt type", default="select", type=str)
    parser.add_argument("--prompt_location", dest="prompt_location", help="prompt location", default="user", type=str)
    parser.add_argument("--max_round", dest="max_round", help="max round", default=15, type=int)
    parser.add_argument("--folder", "-f", dest="folder", help="saving folder", default="./autotools", type=str)
    parser.add_argument("--cache_folder", "-c", dest="cache_folder", default=".cache", help="cache folder")
    parser.add_argument("--samples_per_category", help="samples per category", default=20, type=int)
    parser.add_argument("--temperature", "-t", dest="temperature", help="temperature", default=1, type=float)
    parser.add_argument("--test_run", help="test run", action="store_true")
    parser.add_argument("--categories", dest="categories", help="categories", default=[0, 1], nargs="+")
    parser.add_argument("--seed", dest="seed", help="seed", default=41, type=int)
    parser.add_argument("--select", action="store_true")
    parser.add_argument("--refine", action="store_true")
    parser.add_argument("--sample_all", help="samples per category", default=0, type=int)
    parser.add_argument("-systype", dest="systype", help="system type", default="s0", type=str)
    args = parser.parse_args()
    args.folder = (
        args.folder + args.systype + "_" + args.prompt_location + "_" + args.prompt_type + "_t" + str(args.temperature)
    )
    if args.seed != 41:
        args.folder = args.folder + "_seed" + str(args.seed)
    if args.refine:
        args.folder = args.folder.replace("_t" + str(args.temperature), "_refine_t" + str(args.temperature))
    if args.sample_all != 0:
        args.folder += "_random_sample"
    os.makedirs(args.folder, exist_ok=True)
    return args


def pseudo_main(config_list):
    # 2. args, settings and logger
    args = parse_args()
    args.model = "gpt-4"
    oai.ChatCompletion.request_timeout = 60 * 10  # 10 minutes
    oai.ChatCompletion.set_cache(seed=args.seed, cache_path_root=args.cache_folder)
    logger = mylogger(os.path.join(args.folder, "log.txt"))

    # 3. load math dataset
    problem_sets = load_level5_math_test_each_category(
        samples_per_category=args.samples_per_category, category_to_load=args.categories
    )
    if args.test_run:
        problem_sets = load_level5_math_test_each_category(samples_per_category=1, category_to_load=args.categories)
        logger.log("Take out 1 problem from each category for test run.")

    if args.select:
        problem_sets = load_fixed()

    if args.sample_all != 0:
        problem_sets = random_sample_MATH(args.sample_all)

    print(f"Running {args.folder}")

    selected_samples = {
    }

    # 4. solve
    mathchat_solver = MathChat(
        config_list=config_list,
        model=args.model,
        prompt_type=args.prompt_type,
        sys_type=args.systype,
        max_round=args.max_round,
        temperature=args.temperature,
        prompt_location=args.prompt_location,
        logger=logger,
        refine=args.refine,
    )
    with open(os.path.join(args.folder, "prompt.txt"), "w") as f:
        f.write(mathchat_solver.prompt)

    for problem_set in problem_sets:
        for i in range(len(problem_set)):
            problem_set[i]["problem_id"] = str(i)  # assign problem id
        if args.select:
            if problem_set[0]["type"] in selected_samples and len(selected_samples[problem_set[0]["type"]]) > 0:
                problem_set = [problem_set[i] for i in selected_samples[problem_set[0]["type"]]]
                print(problem_set[0]["type"], selected_samples[problem_set[0]["type"]])
            else:
                continue
        mathchat_solver.solve_one_category(problem_set, saving_folder=args.folder)
        # os.system("tar -czf " + args.folder + ".tar.gz " + args.folder)

    logger.log("****************************\n\n\n\n\n", verbose=False)
    os.system("tar -czf " + args.folder + ".tar.gz " + args.folder)