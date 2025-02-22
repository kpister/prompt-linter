import sys, os, json, re, random
import pandas as pd
from tqdm.auto import tqdm, trange
import torch
from llm_async import run_llm_coroutine
import sys

INTERPOLATE_VAR = "{TEXT}"
PWD = "./"

# 26 prompt principles
PROMPT_PRINCIPLES = """No need to be polite with LLM so there is no need to add phrases like "please", "if you don't mind", "thank you", "I would like to", etc., and get straight to the point.
####Integrate the intended audience in the prompt, e.g., the audience is an expert in the field.
####Break down the complex tasks into a sequence of simpler prompts in an interactive conversation.
####Employ affirmative directives such as 'do,' while steering clear of negative language like 'don't'.
####When you need clarity or a deeper understanding of a topic, idea, or any piece of information, utilize the following prompts:
        - Explain [insert specific topic] in simple terms.
        - Explain to me like I'm 11 years old.
        - Explain to me as if I'm a beginner in [field].
        - Write the [essay/text/paragraph] using simple English like you're explaining something to a 5-year-old.
####Add "I'm going to tip $xxx for a better solution!"
####Implement example-driven prompting (Use few-shot prompting).
####When formatting your prompt, start with '###Instruction###', followed by either '###Example###* or '###Question###' if relevant. Subsequently, present your content. Use one or more line breaks to separate instructions, examples, questions, context, and input data.
####Incorporate the following phrases: "Your task is" and "You MUST".
####Incorporate the following phrases: "You will be penalized".
####Use the phrase "Answer a question given in a natural, human-like manner" in your prompts.
####Use leading words like writing "think step by step”.
####Add to your prompt the following phrase "Ensure that your answer is unbiased and does not rely on stereotypes".
####Allow the model to elicit precise details and requirements from you by asking you questions until he has enough information to provide the needed output (for example, "From now on, I would like you to ask me questions to...").
####To inquire about a specific topic or idea or any information and you want to test your understanding, you can use the following phrase: "Teach me the [Any theorem/topic/rule name] and include a test at the end, but don't give me the answers and then tell me if I got the answer right when I respond".
####Assign a role to the large language models.
####Use Delimiters.
####Repeat a specific word or phrase multiple times within a prompt.
####Combine Chain-of-thought (CoT) with few-Shot prompts.
####Use output primers, which involve concluding your prompt with the beginning of the desired output. Utilize output primers by ending your prompt with the start of the anticipated response.
####To write an essay/text/paragraph/article or any type of text that should be detailed: "Write a detailed [essay/text/paragraph] for me on [topic] in detail by adding all the information necessary".
####To correct/change specific text without changing its style: "Try to revise every paragraph sent by users. You should only improve the user's grammar and vocabulary and make sure it sounds natural. You should not change the writing style, such as making a formal paragraph casual".
####When you have a complex coding prompt that may be in different files: "From now and on whenever you generate code that spans more than one file, generate a [programming language ] script that can be run to automatically create the specified files or make changes to existing files to insert the generated code. [your question]".
####When you want to initiate or continue a text using specific words, phrases, or sentences, utilize the following prompt:
        - I'm providing you with the beginning [song lyrics/story/paragraph/essay...]: [Insert lyrics/words/sentence]'. Finish it based on the words provided. Keep the flow consistent.
####Clearly state the requirements that the model must follow in order to produce content, in the form of the keywords, regulations, hint, or instructions
####To write any text, such as an essay or paragraph, that is intended to be similar to a provided sample, include the following instructions:
        - Please use the same language based on the provided paragraph[/title/text/essay/answer].
"""
PRINCIPLE_SAMPLE_COUNT = 5
principles = PROMPT_PRINCIPLES.split('####')
random.seed(42)


# SEED PROMPTS
async def get_seed_prompts(CHOSEN_PROMPT, request_count=5):
    prompt_template = """Here are {PRINCIPLE_SAMPLE_COUNT} prompt principles:

{sampled_principles}

Act like a highly skilled prompt engineer. Your task is to create the best prompt possible using the list 26 principles from the list above.

Follow these tasks step-by-step:

Step 1: Read the entire list of 26 prompt principles. Analyze and explain each one of those 26 prompting principles.

Step 2: Create a prompt using those 26 prompting principles for the following prompt that's delimited by "####". Like the following prompt, make sure the new prompt contains exactly one interpolable variable "{INTERPOLATE_VAR}".

####
{CHOSEN_PROMPT}
####

Respond with a JSON object containing two keys "step1" and "step2", respectively mapping to the analysis and explanation to the 26 prompting principles and the prompt you created.

Example JSON object:
{{
    "step1": \"\"\"Here is the analysis and explanation for each of the 26 prompting principles...\"\"\",
    "step2": \"\"\"Think step by step...\"\"\"
}}

Take a deep breath and work on this problem step-by-step. Return only the JSON object with the keys "step1" and "step2", and nothing else. Nothing but JSON."""
    has_correct_keywords = lambda prompt: re.findall(r"{(.*?)}", prompt) == [INTERPOLATE_VAR[1:-1]]
    new_prompts = [CHOSEN_PROMPT]  # The SEED PROMPTS INCLUDES THE CHOSEN PROMPT
    pbar = tqdm(total=request_count, desc="Generating Seed Prompts")
    pbar.update(1)  # Update the progress bar for the chosen prompt
    while len(new_prompts) < request_count:
        prompts = []
        for _ in range(request_count):
            # Sampling and interpolating 5-randomly sampled principles
            selected_principles_lst = random.sample(principles, PRINCIPLE_SAMPLE_COUNT)
            sampled_principles = ""
            for i, principle in enumerate(selected_principles_lst):
                sampled_principles += f"{i+1}. {principle}"
            prompt = prompt_template.format(
                PRINCIPLE_SAMPLE_COUNT=PRINCIPLE_SAMPLE_COUNT,
                sampled_principles=sampled_principles,
                CHOSEN_PROMPT=CHOSEN_PROMPT,
                INTERPOLATE_VAR=INTERPOLATE_VAR
            )
            prompts.append(prompt)

        temperatures = [i/len(prompts) for i in range(len(prompts), 0, -1)]  # Varying temperature to diversity responses (decreasing order so that temp is high when polling)
        responses = await run_llm_coroutine(prompts, temperature=temperatures, respond_json=True, model="gpt-4o", msg="Generating Seed Prompts - 20 calls")
        for res in responses:
            try:
                new_prompt = eval(res)["step2"]
                assert has_correct_keywords(new_prompt)
                new_prompt.format(TEXT="PLACEHOLDER")  # Check if the prompt is valid
                new_prompts.append(new_prompt)
                pbar.update(1)
            except Exception as e:
                print(f"Error: {e}")
                print(f"Response: {res}")
                continue
    pbar.close()
    return new_prompts[:request_count]


def check_and_reformat(prompt):
    """
    Checks if prompt is valid. If prompt is valid, returns a slightly modified prompt that can be evaluated and optimized.
    """
    pattern1 = r"{[^}]*}"
    pattern2 = "PLACEHOLDER"
    matches1 = re.findall(pattern1, prompt)
    condition1 = len(matches1) == 1 
    condition2 = prompt.count(pattern2) == 1
    
    if not condition1 and not condition2:
        print(prompt)
    
    # Reformat the prompt
    if condition1:
        return prompt.replace(matches1[0], INTERPOLATE_VAR)
    elif condition2:
        return prompt.replace(pattern2, INTERPOLATE_VAR)
    
    raise ValueError("Invalid prompt format. Prompt must contain some str/var to be interpolated.")


# Generate a question and answer pair using a language model
async def generate_synthetic_data(CHOSEN_PROMPT, sample_size=40):
    # Check if the synthetic data already exists
    SYNTHETIC_DATA_FILEPATH_ASYNC = f"{PWD}synthetic_dataset.json"
    if os.path.exists(SYNTHETIC_DATA_FILEPATH_ASYNC):
        # Reading saved data
        with open(SYNTHETIC_DATA_FILEPATH_ASYNC, "r") as f:
            text = json.load(f)
        return text

    async def generate_synthetic_datapoint(request_count):
        data_generation_principles = [
            "Generate text and response that is in the format shown below and highly relevant to the prompt. Take a deep breath and think step-by-step.",
            "Think out of the box and generate text and response that is incredibly unique while being relevant to the prompt.",
            "Generate text and response from the perspective of an expert in the field related to the prompt.",
            "Create a text and response that reflects the thoughts and feelings of a person directly affected by the prompt.",
            "Generate text and response that explains the prompt using an analogy from a different domain or field.",
            "Generate text and response that involves connections between multiple concepts related to the prompt.",
            "Generate text and response that presents a contrarian view on the prompt, highlighting potential flaws or limitations.",
            "Think about different scenarios and generate text and response that explores the implications of the prompt in various contexts.",
            "Create a text and response that applies a theoretical framework or abstract concept to the prompt, providing new insights or perspectives.",
            "Generate text and response that describes a real-world scenario or application where the prompt is relevant or useful.",  # 10
            "Consider all aspects of the prompt and generate text and response that addresses each component comprehensively.",
            "Imagine a conversation between two people discussing the prompt and generate text and response that captures the dialogue.",
            "Put yourself in the shoes of someone encountering the prompt for the first time and generate text and response that reflects their initial thoughts and questions.",
            "Reflect on the historical context or background of the prompt and generate text and response that incorporates relevant historical information.",
            "Apply a creative or artistic lens to the prompt and generate text and response that is imaginative and visually engaging.",
            "Zoom in on a specific detail or aspect of the prompt and generate text and response that explores it in depth.",
            "Zoom out to a broader perspective and generate text and response that considers the larger implications or significance of the prompt.",
            "Generate text and response that incorporates humor, wit, or satire to add a lighthearted or entertaining element to the prompt.",
            "Question the assumptions underlying the prompt and generate text and response that challenges or reconsiders those assumptions.",
            "Explore the prompt from a cross-cultural or global perspective and generate text and response that considers how different cultures or societies might interpret it.",  # 20
            "Think about the ethical implications of the prompt and generate text and response that addresses the ethical considerations involved.",
            "Consider the prompt from a scientific or technical standpoint and generate text and response that applies scientific principles or technical knowledge to the prompt.",
            "Put yourself in the position of an educator teaching a class about the prompt and generate text and response. Text is to be interpolated in the prompt. Response is the expected response to the prompt with the text interpolated.",
            "Apply a philosophical or theoretical framework to the prompt and generate text and response that explores the philosophical implications or theoretical underpinnings of the prompt.",
            "Juxtapose the prompt with a seemingly unrelated concept or idea and generate text and response that draws connections between the two.",
            "Keep the prompt in mind and generate text and response that is highly relevant to the prompt. Think step by step.",
            "Look at the prompt from a different angle and generate text and response that offers a fresh perspective or new insights.",
            "X-ray the prompt and generate text and response that delves deep into the core of the prompt, uncovering hidden meanings or underlying assumptions.",
            "Create a text and response that is engaging and thought-provoking, encouraging the reader to think critically about the prompt.",
            "Navigate the complexities of the prompt and generate text and response that navigates the complexities of the prompt, providing clarity and insight.",  # 30
        ]
        
        
        SYNTH_DATA_GEN_PROMPT = """You are a helpful assistant designed to generate synthetic data for the prompt: "{CHOSEN_PROMPT}".
Please generate a text and response pair for the prompt. Text is to be interpolated in the prompt. Response is the expected response to the prompt with the text interpolated.
Ensure that the text is delimited by <BEGIN_TEXT> and <END_TEXT> and the response is delimited by <BEGIN_RESPONSE> and <END_RESPONSE>. 

{prompt_guide}

## Example Format:
<BEGIN_PROMPT> This is the prompt provided <END_PROMPT>
<BEGIN_TEXT> This is the text to be interpotated into the prompt. <END_TEXT>
<BEGIN_RESPONSE> The response to be generated from the text-interpolated prompt. <END_RESPONSE>

## Query:
<BEGIN_PROMPT> {CHOSEN_PROMPT} <END_PROMPT>
"""
        data_pairs = []
        unique_data = set()

        pbar = tqdm(total=request_count, desc="Generating Synthetic Data")
        attempt_count = 0
        while len(data_pairs) < request_count and attempt_count < 25:
            attempt_count += 1
            print(f"Attempt {attempt_count} made.")
            random_principles = [random.choice(data_generation_principles) for _ in range(request_count)]
            data_gen_prompts = [SYNTH_DATA_GEN_PROMPT.format(CHOSEN_PROMPT=CHOSEN_PROMPT, prompt_guide=random_principles[i]) for i in range(request_count)]
            temperatures = [(i/len(data_gen_prompts)) * 1.2 for i in range(len(data_gen_prompts), 0, -1)]  # Varying temperature to diversity responses (decreasing order so that temp is high when polling)
            response = await run_llm_coroutine(data_gen_prompts, temperature=temperatures, model="gpt-4o", msg="Generating Synthetic Data - 100 calls")
            for i, res in enumerate(response):
                print(res)
                try:
                    # Checking if the response is valid
                    text_match = re.search(r"<BEGIN_TEXT>([\s\S]*?)<END_TEXT>", res)
                    response_match = re.search(r"<BEGIN_RESPONSE>([\s\S]*?)<END_RESPONSE>", res)
                    assert text_match is not None and response_match is not None, "Invalid response format."
                    text = text_match.group(1).strip()
                    response = response_match.group(1).strip()
                    assert text not in unique_data, "Data already exists in the set."
                    unique_data.add(text)
                    data_pairs.append({"text": text, "response": response})
                    # TODO: Reinforcing the prompt principle, maybe???
                    # data_generation_principles.append(random_principles[i])
                    pbar.update(1)
                except Exception as e:
                    print(e)
                    # print(res)
                    continue
        pbar.close()
        return data_pairs[:request_count]

    # Generating synthetic data
    text = await generate_synthetic_datapoint(sample_size)

    # Saving to file as json
    with open(SYNTHETIC_DATA_FILEPATH_ASYNC, "w") as f:
        json.dump(text, f)

    return text


# Scoring the instruction using the sample
# Scoring the instruction using the sample
async def opt_llm(prompt_score_pairs, request_count=8):
    has_correct_keywords = lambda prompt: re.findall(r"{(.*?)}", prompt) == [INTERPOLATE_VAR[1:-1]]
    # Format the instruction and score pairs into a string
    pairs_str = ""
    for ins, score in prompt_score_pairs.items():
        pairs_str += f"text:\n{ins}\nscore:\n{score:.2f}\n\n"

    prompt = f"""You're a highly skilled prompt engineer and a prompt optimization expert. 
The user has some prompts along with their corresponding scores. 
Your task is to generate a new prompt that scores as high as possible. Do not generate its corresponding score. 

Here are some prompts along with their corresponding scores. The texts are arranged in ascending order
based on their scores, where higher scores indicate better quality.

{pairs_str}

Write your new text that is different from the old ones and has a score as high as possible. Ensure that the generated 
instruction has "{INTERPOLATE_VAR}" so the user can replace it with the text to be interpolated. Think step by step. 
Generate only the text. Do not include the scores. Delimit the your suggested text by <BEGIN_ANSWER> and </END_ANSWER>.
"""
    new_prompts = []
    pbar = tqdm(total=request_count, desc="Optimizing")
    while len(new_prompts) < request_count:
        responses = await run_llm_coroutine([prompt for _ in range(request_count)], temperature=1.0, model="gpt-4o", msg="Optimizing - 20 calls")
        for res in responses:
            try:
                match = re.search(r'<BEGIN_ANSWER>(.*?)</END_ANSWER>', res, re.DOTALL)
                assert match is not None, "No match found for <BEGIN_ANSWER> and </END_ANSWER> tags"
                extracted_text = match.group(1)
                assert has_correct_keywords(extracted_text), "Extracted text does not have correct keywords"
                new_prompts.append(extracted_text)
                pbar.update(1)
            except Exception as e:
                # print(e)
                continue
    pbar.close()
    return new_prompts[:request_count]


async def create_scoring_prompt(prompt, sample_data):
    """
    Given a prompt and sample data, generates a scoring prompt for the prompt.
    """    
    prompt_template = f"""Write a scoring prompt for an example input output pair on a prompt to a language model. 
Use the variable name output for the output of the prompt. 

### Rules ###
- The scoring prompt must contain the "{{output}}" variable and "{{text}}" variable. Ensure that both variables are present in the scoring prompt criteria.
- Your answer should be inside <BEGIN_CRITERIA> and <END_CRITERIA> constructs.

## Example:
<BEGIN_PROMPT> 'what is a fruit of color: {{TEXT}}. Return the name of the fruit and nothing else:' <END_PROMPT>
<BEGIN_EXAMPLE_INPUT> {{"text": "yellow", "output": "banana"}} <END_EXAMPLE_INPUT>
<BEGIN_CRITERIA> Is a "{{output}}" this color: "{{text}}"? Answer yes or no only. <END_CRITERIA>

## Query:
<BEGIN_PROMPT> {prompt} <END_PROMPT>
<BEGIN_EXAMPLE_INPUT> {sample_data} <END_EXAMPLE_INPUT>"""

    # Extract the scoring prompt
    for i in range(10):
        try:
            # Generate Scoring Prompt
            res = await run_llm_coroutine([prompt_template], model="gpt-4o", temperature=1.0)
            res = res[0]

            # Extract Criteria
            match = re.search(r'<BEGIN_CRITERIA>(.*?)<END_CRITERIA>', res, re.DOTALL)
            assert match is not None, "No match found for <BEGIN_CRITERIA> and <END_CRITERIA> tags"
            extracted_text = match.group(1).strip()
            
            # Check if extracted text has the correct keywords
            matches = re.findall(r"{[^}]*}", extracted_text)
            assert matches is not None, "No matches found for variables in prompt"
            assert len(matches) == 2, "Prompt does not contain the correct number of variables"
            for m in matches:
                if m.lower() == "{text}":
                    extracted_text = extracted_text.replace(m, "{text}")
                elif m.lower() == "{output}":
                    extracted_text = extracted_text.replace(m, "{output}")
            assert "{text}" in extracted_text and "{output}" in extracted_text, "Prompt does not contain the correct keywords"
            return extracted_text
        except AssertionError as e:
            print(e, f"Prompt: {extracted_text}")
            print(f"Generating new scoring prompt. Attempt {i+1} failed.")
        
    raise ValueError("Scoring Prompt could not be generated.")


async def score(prompts, testing_sample, scoring_prompt):
    """
    Score the instruction using the sample.

    Args:
    instruction: str
    sample: Dataset with "question" and "answer" as keys

    Returns:
    accuracy: float
    """
    prompt_score_pairs = {}
    for prompt in tqdm(prompts, desc="Scoring"):
        accuracy = 0
        prompt_interpolated = [prompt.format(TEXT=data_pair["text"]) for data_pair in testing_sample]
        generated_response = await run_llm_coroutine(prompt_interpolated, temperature=0.0, model="gpt-4o-mini", msg="Scoring - 30 calls mostly")
        scoring_prompt_interpolated = [scoring_prompt.format(output=generated_response[i], text=data_pair["text"]) for i, data_pair in enumerate(testing_sample)]
        prompt_scores = await run_llm_coroutine(scoring_prompt_interpolated, temperature=0.0, model="gpt-4o", max_tokens=5, msg="Scoring - 30 calls mostly")
        print(prompt_scores)
        assert len(generated_response) == len(testing_sample) == len(scoring_prompt_interpolated)
        for i in range(len(generated_response)):
            accuracy += int("yes" in prompt_scores[i].lower())
        prompt_score_pairs[prompt] = accuracy / len(testing_sample) * 100

    return prompt_score_pairs


async def opro(CHOSEN_PROMPT, training_sample, scoring_prompt, STEP_COUNT=8, PROMPTS_PER_STEP=5, MAX_PROMPT_SCORE_PAIRS=20):
    # NOTE: MAX_PROMPT_SCORE_PAIRS  Keep the best 20 prompts at any time
    SAVE_PATH_ASYNC = f"{PWD}training_results.json"
    SEED_PROMPTS_PATH = f"{PWD}seed_prompts.json"
    SEED_PROMPTS_COUNT = 16
    SEED_PROMPTS = None
    best_scores = []
    
    # loading seed prompts
    if os.path.exists(SEED_PROMPTS_PATH):
        with open(SEED_PROMPTS_PATH, "r") as f:
            SEED_PROMPTS = json.load(f)
    else:
        SEED_PROMPTS = await get_seed_prompts(CHOSEN_PROMPT, request_count=SEED_PROMPTS_COUNT)
        SEED_PROMPTS = [check_and_reformat(prompt) for prompt in SEED_PROMPTS]
        with open(SEED_PROMPTS_PATH, "w") as f:
            json.dump(SEED_PROMPTS, f)

    # loading saved data
    if os.path.exists(SAVE_PATH_ASYNC):
        with open(SAVE_PATH_ASYNC, "r") as f:
            results = json.load(f)  # {step0: {prompt1: score1, prompt2: score2, ...}, step1: {...}, ...}
        return results
    else:
        # Scoring the seed prompts
        prompt_score_pairs = await score(SEED_PROMPTS, training_sample, scoring_prompt)
        # Sort by score
        prompt_score_pairs = dict(
            sorted(
                prompt_score_pairs.items(), key=lambda x: x[1], reverse=True
            )
        )
        best_scores.append(max(prompt_score_pairs.values()))
        results = {"0": prompt_score_pairs}
        with open(SAVE_PATH_ASYNC, "w") as f:
            json.dump(results, f)

    # Each step takes aboy 5 to 10 minutes with gemma:2b
    for i in range(1, STEP_COUNT + 1):
        # If the max score is reached, exit
        if max(prompt_score_pairs.values()) == 100:
            print("Max score reached. Exiting...")
            print(f"Current Best score: {max(prompt_score_pairs.values())}")
            print(f"Current Best prompt: {max(prompt_score_pairs, key=prompt_score_pairs.get)}")
            print("\n")
            break
        
        # Continue optimizing
        print(f"Step {i}")
        while True:
            try:
                # Optimizer LLM
                instructions = await opt_llm(prompt_score_pairs, request_count=PROMPTS_PER_STEP)

                # Scoring the new instructions
                new_ins_score_pairs = await score(instructions, training_sample, scoring_prompt)
                combined_ins_score_pairs = {**prompt_score_pairs, **new_ins_score_pairs}
                prompt_score_pairs = dict(
                    sorted(
                        combined_ins_score_pairs.items(), key=lambda x: x[1], reverse=True
                    )[:MAX_PROMPT_SCORE_PAIRS]
                )

                # Saving data
                results[f"{i}"] = prompt_score_pairs
                with open(SAVE_PATH_ASYNC, "w") as f:
                    json.dump(results, f)
                
                # Printing the best prompt and score for the current step
                best_prompt = max(prompt_score_pairs, key=prompt_score_pairs.get)
                best_score = prompt_score_pairs[best_prompt]
                best_scores.append(best_score)

                print(f"Step {i} completed.")
                print(f"Current Best score: {best_score}")
                print(f"Current Best prompt: {best_prompt}")
                print("\n")

                break
            except ValueError as e:
                print(e)
            except Exception as e:
                print(e)
        
        # Early stopping if the score doesn't improve for 3 consecutive steps

        if len(best_scores) > 3:
            print("Best Scores: ", best_scores[-3:])
            if best_scores[-1] == best_scores[-2] == best_scores[-3]:
                print("Early stopping...")
                break
    
    return results

# OPRO for summarization prompts
async def qarefinement_opro(prompt, cache_dir="0", TRAINING_SAMPLE_SIZE=30, TESTING_SAMPLE_SIZE=70, PROMPTS_PER_STEP=20, STEP_COUNT=15, MAX_PROMPT_SCORE_PAIRS=10):
    global PWD, CHOSEN_PROMPT
    CHOSEN_PROMPT = check_and_reformat(prompt)
    PWD = os.path.join(".", cache_dir) + "/"
    
    # If dir doesn't exist, create it
    if not os.path.exists(PWD):
        os.mkdir(PWD)
        
    # Open the file and set sys.stdout to the file object
    sys.stdout = open(f'{PWD}logs.txt', 'w')

    # Generate synthetic data
    synthetic_data = await generate_synthetic_data(
        CHOSEN_PROMPT, sample_size=TRAINING_SAMPLE_SIZE + TESTING_SAMPLE_SIZE
    )

    # Train-Test Split
    training_sample = synthetic_data[:TRAINING_SAMPLE_SIZE]
    testing_sample = synthetic_data[
        TRAINING_SAMPLE_SIZE : TRAINING_SAMPLE_SIZE + TESTING_SAMPLE_SIZE
    ]
    
    # Get Scoring Prompt
    scoring_prompt = ""
    if os.path.exists(f"{PWD}scoring_prompt.txt"):
        with open(f"{PWD}scoring_prompt.txt", "r") as f:
            scoring_prompt = f.read()
    else:
        scoring_prompt = await create_scoring_prompt(CHOSEN_PROMPT, {'text': testing_sample[0]["text"], 'output': testing_sample[0]["response"]})
        with open(f"{PWD}scoring_prompt.txt", "w") as f:
            f.write(scoring_prompt)
    
    # OPRO
    opro_results = await opro(CHOSEN_PROMPT, training_sample, scoring_prompt, STEP_COUNT=STEP_COUNT, PROMPTS_PER_STEP=PROMPTS_PER_STEP, MAX_PROMPT_SCORE_PAIRS=MAX_PROMPT_SCORE_PAIRS)
    best_prompt = max(opro_results[str(len(opro_results)-1)], key=opro_results[str(len(opro_results)-1)].get)

    # Comparing the initial prompt with the optimized prompt
    print("Calculating Test Scores...")
    result = {
        "initial_prompt": await score([CHOSEN_PROMPT], testing_sample, scoring_prompt),
        "optimized_prompt": await score([best_prompt], testing_sample, scoring_prompt),
    }

    # Printing Test Scores
    print("Printing Test Scores:")
    print(f"Initial Prompt Score: {result['initial_prompt']}")
    print(f"Optimized Prompt Score: {result['optimized_prompt']}")
    
    # Reset sys.stdout to its original state
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    return result
