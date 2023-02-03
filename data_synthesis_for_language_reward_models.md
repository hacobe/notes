# Data synthesis for language reward models

## Introduction

Quality estimation is the task of estimating the quality of a prediction from a model without access to a reference output. Applications include communicating information about quality to a user, abstaining from returning a prediction if the quality is sufficiently low, and using estimates of quality to train a new model with better performance.

A language reward model is a language model used to predict the quality of the output of another language model. It is called a reward model, because it usually appears in the context of training a language model with reinforcement learning to generate outputs that maximize the reward given by the language reward model.

For many tasks, it is difficult to programmatically assess the quality of a language model’s output. Instead, the gold standard approach is to have humans evaluate that output. However, collecting these human judgments is expensive and reward models trained on judgments in one domain may not generalize well to other domains.

To address these problems, we investigate strategies to synthesize training datasets for language reward models. We use a large dataset of human preferences over summaries of Reddit posts introduced in [Stiennon et al 2020](https://arxiv.org/pdf/2009.01325.pdf). We train language reward models on completely synthetic training datasets and evaluate them on the human preference data. We also compare the performance to reward models trained on the human preference data.

The code to reproduce these analyses is [here](https://github.com/hacobe/rusp/tree/main/data_synthesis).

## Related work

There is a large literature on quality estimation for machine translation. For several years, the EMNLP conference on machine translation has run quality estimation contests. In 2021, one of the best performing methods ("C-SPEC" in [Freitag et al 2021](https://aclanthology.org/2021.wmt-1.73.pdf)) used a data augmentation strategy that involved simulating translation errors ([Takahashi et al 2021](https://aclanthology.org/2021.wmt-1.113.pdf)) by replacing words in a reference translation with their antonyms or by changing the gender of words.

[Tuan et al 2021](https://aclanthology.org/2021.eacl-main.50.pdf) also explored data augmentation strategies for machine translation without human labeled data. They take a candidate translation, align it to a reference translation, and train on the token-level error labels. The candidate translations are produced either by using a translation model or by taking a reference translation and rewriting it to include errors using a masked language model.

[Fomicheva et al 2020](https://arxiv.org/pdf/2005.10608.pdf) explore different unsupervised quality estimation methods for machine translation that do not require training an auxiliary model. Instead, the quality estimates are derived from the translation model itself.

Stiennon et al 2020 showed that summarization models trained with reinforcement learning from human preferences can generate summaries of Reddit posts that are rated more highly by human raters than the original summaries written by the authors of the posts.

Reinforcement learning from human preferences has been applied to several language modeling tasks. [Bai et al 2022](https://arxiv.org/abs/2204.05862) and [Glaese et al 2022](https://arxiv.org/abs/2209.14375) apply it to train dialogue agents. [Menick et al 2022](https://storage.googleapis.com/deepmind-media/Teaching%20language%20models%20to%20support%20answers%20with%20verified%20quotes/Teaching%20language%20models%20to%20support%20answers%20with%20verified%20quotes.pdf) uses it to train a question and answering system that cites its sources. [Askell et al 2021](https://arxiv.org/pdf/2112.00861.pdf) study how ranked preference modeling, imitation learning and binary discrimination scale on several tasks. They also show that preference model pre-training can improve the performance of preference models.

[Fabbri et al 2020](https://arxiv.org/pdf/2007.12626.pdf) evaluates various reference-based and reference-less quality metrics on a dataset of human judgments of the coherence, consistency, fluency, and relevance of model-generated summaries of CNN/DailyMail news articles. The reference-less methods include SummaQA ([Scialom et al 2019](https://arxiv.org/pdf/1909.01610.pdf)), BLANC ([Vasilyev et al 2020](https://arxiv.org/pdf/2002.09836.pdf)) and SUPERT ([Gao et al 2020](https://arxiv.org/pdf/2005.03724.pdf)). SUPERT is designed for multi-document summarization. QuestEval (Scialom et al 2021) is a more recent version of SummaQA. A recent study ([Deutsch et al 2022](https://arxiv.org/pdf/2210.12563.pdf)) uses SummaQA and criticizes the use of model-based approaches to evaluation.

[Gleave and Irving 2022](https://arxiv.org/pdf/2203.07472.pdf) explore uncertainty estimation and active learning to improve the sample efficiency and robustness of language reward models. They also use the TL;DR dataset introduced in Stiennon et al 2020. However, they use the entire dataset with the given "train", "valid1" and "valid2" splits. Those splits are not used to train and evaluate reward models in Stiennon et al 2020. Instead, subsets of the dataset are used (Table 11). The splits used in Gleave and Irving 2022 are challenging since most of the "train" split consists of summaries from models that do not use any human preference data and the "valid1" and "valid2" splits include summaries from models that have been trained with multiple rounds of reinforcement learning from human preferences. The difficulty of generalizing from preferences between low quality summaries to preferences between high quality summaries could partially explain the negative result in Gleave and Irving 2022.

A closely related literature is on selective prediction and error detection. [Hendrycks and Gimpel 2018](https://arxiv.org/abs/1610.02136) analyzed the simple baseline of using the Maximum Softmax Probability for error detection for classification. [Malinin and Gales 2021](https://arxiv.org/pdf/2002.07650.pdf) explore token-level and sequence-level error detection for automatic speech recognition and machine translation using statistics derived from the predictive probability distribution of an ensemble of sequence models. [Ren et al 2022](https://arxiv.org/pdf/2209.15558.pdf) use the Mahalanobis distance in the space of transformer embeddings and the sequence probability for selective translation and summarization.

## Methods

We used the filtered TL;DR reference summaries dataset and the TL;DR human preferences dataset introduced in Stiennon et al 2020. Each example in the TL;DR reference summaries dataset consists of a Reddit post and a reference summary written by the author of the post. Each example in the TL;DR human preferences dataset consists of a Reddit post, a pair of summaries generated by different policies (including summaries from models of varying quality and reference summaries), and a label that indicates which summary was preferred by a human rater. We collected all the unique prompts (the formatted concatenation of the subreddit, title and post) in these 2 datasets and randomly selected a subset as the held-out prompts for our experiments. We fine-tuned pre-trained GPT2 models of different scales on the training split of the TL;DR reference summaries dataset for 1 epoch with the default HuggingFace parameters. We generated summaries from these models using greedy decoding with a max length of 48 tokens. As a sanity check, we compared performance on the test split of the reference summaries dataset to results reported in Stiennon et al 2020. We found ROUGE-1 F-scores that look a few points better than the scores reported in that paper (Figure 14a reports ~100 million parameter model with a ROUGE score a little above ~0.225 and ~1 billion with a ROUGE score a little above ~0.25).

Table: ROUGE scores for pre-trained GPT2 models fine-tuned on the training split of the TL;DR reference summaries dataset and evaluated on the test split.
| Summarization model | ROUGE |
| ------------------- | ----- |
| GPT2 117M | 0.2765 |
| GPT2 345M | 0.2876 |
| GPT2 774M | 0.2921 |
| GPT2 1.5B | 0.2973 |

We then added a reward head on top of each summarization model and fine-tuned the resulting model for 1 epoch with a learning rate of 1.5e-5 decaying with a cosine schedule and a warm up ratio of 5% (following Stiennon et al 2020). We evaluated the AUC and accuracy on the “valid2” split of the human preferences dataset and found results comparable to the results reported in Stiennon et al 2020 and in Gleave and Irving 2022 (see Table 2). For example, Gleave and Irving 2022 reported an accuracy of 64.84% +/- 1.63% for a 1.3B parameter reward model compared to our accuracy of 65.86% for a 1.5B parameter reward model.

Table: AUC and accuracy for reward models on the "valid2" split of the human preferences dataset.
| Reward model | AUC | Accuracy |
| ------------ | --- | -------- |
| GPT2 117M | 0.6689 | 0.6202 |
| GPT2 345M | 0.6784 | 0.6332 |
| GPT2 774M | 0.6989 | 0.6469 |
| GPT2 1.5B | 0.7187 | 0.6592 |


Stiennon et al 2020 performed multiple rounds of reinforcement learning from human feedback (RLHF) to train their language reward models. We simulated the first round of this process by creating a new training and test split for the human preferences dataset consisting only of (a) comparisons between the reference summaries and summaries sampled from the "sup1" supervised model trained in the paper ("ref vs. sup1"), (b) comparisons between reference summaries and summaries sampled from the "sup2" supervised model trained in the paper ("ref vs. sup2"), (c) comparisons between summaries sampled from the "sup1" supervised model ("sup1 vs. sup1") and (d) comparisons between summaries sampled from the "sup2" supervised model ("sup2 vs. sup2"). The resulting dataset excludes summaries from models that used human feedback for training, which we would not have access to in the first round of the RLHF training process. We trained reward models on the training split of this dataset and evaluated on the test split. We also trained reward models on synthetic datasets, while still evaluating on the same test split.

Table: "First round" human preferences dataset.
| Split | No. of prompts | No. of comparisons |
| ----- | -------------- | ------------------ |
| Train | 8,519 | 40,843 |
| Test | 2,000 | 9,638 |


Table: Policy composition of test split of “First round” human preferences dataset.
| Policy comparison | No. of comparisons |
| ----------------- | ------------------ |
| ref vs sup2 | 3,384 |
| sup2 vs sup2 | 2,984 |
| ref vs sup1 | 1,706 |
| sup1 vs sup1 | 1,564 |

The synthetic datasets consist of comparisons between the following types of summaries:
* ref: Reference summaries
* gpt2: Summaries generated from the language model with greedy decoding.
* gpt2d0.2: Summaries generated from the language model with greedy decoding and with a dropout probability of 20% in all the dropout layers (double the dropout probability used during training).
* maskedrefprompt: We took reference summaries and in each summary replaced a random contiguous span comprising 25% of the tokens with a single mask token.[^1] We then fine-tuned a language model (initialized with the summarization model parameter values) on 10K examples to recover the full reference summary given only the subreddit and the masked summary. The "maskedrefprompt" summaries are summaries generated from this fine-tuned language model.
* shuffledprompt: Summaries generated from the language model with greedy decoding but with sentences in the post randomly shuffled.

## Results

The figure below shows the results for the 117M parameter GPT-2 model. The black line is the reward model trained on human preferences. The other lines are reward models trained on the synthetic datasets.

![data_synthesis_gpt2](/img/data_synthesis_gpt2.png)

We found that ref vs. maskedrefprompt comparisons and gpt2 vs. gpt2d0.2 comparisons performed the best out of the synthetic datasets. The reward model trained on ref vs. maskedrefprompt comparisons achieves similar performance to the reward model trained on 30,000 human preferences.

The figure below shows the results for the 1.5B parameter GPT-2 model.

![data_synthesis_gpt2_xl](/img/data_synthesis_gpt2_xl.png)

The reward model trained on ref vs. maskedrefprompt comparisons provides a smaller benefit compared to collecting human preference data, because the larger language model is more sample efficient. Specifically, the reward model trained on ref vs. maskedrefprompt comparisons achieves similar performance to the reward model trained on 5,000 human preferences.

We also found that a logistic regression baseline using the difference between the number of characters in the summaries and the difference between the longest repeated sequence of tokens in the summaries as features achieved 60% accuracy trained on the full dataset of ~40,000 human preferences.

## Discussion

To make these methods practical, there are two major issues:
* Improving the scaling properties of the synthetic datasets. An advantage of synthetic data is that we can easily generate a lot of it. However, it looks like performance flattens out for the synthetic datasets in our experiments. Are there strategies for generating synthetic data where performance continues improving with more data? One idea is to train the language model that predicts the masked spans of the reference summaries on more examples and with more context to make distinguishing the prediction from the true span in the reference more difficult.
* Applying the method to out-of-domain datasets. The larger the language model, the less the advantage the synthetic datasets seem to provide when evaluating in-domain, because the larger language models are more sample efficient. However, synthetic datasets may still provide an advantage out-of-domain.

## Footnotes

[^1]: We found that replacing each token with a mask token results in summaries that are of similar length as the original reference summary and reward models that do not learn as much about the relationship between summary length and quality. We also found that masking the end of the reference summary and just using the original summarization model to generate the remaining tokens results in very short generations that, for example, simply add a period to the shortened reference summary.
