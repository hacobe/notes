# Selective Sequence Prediction

## Summary

Selective prediction is prediction with the option to abstain on selected examples. It has mostly been studied in the classification setting. Instead, we focus on the structured prediction setting and on automatic speech recognition (ASR) and machine translation (MT) in particular. [Malinin and Gales 2021](https://arxiv.org/abs/2002.07650) reported that the entropy of the predictive probability distribution is the most informative measure of sequence-level error for ASR and MT selective prediction tasks compared to other summary statistics and heuristic methods in the literature. Here, we show that a simple, sample-based estimate outperforms those methods at the cost of additional compute.

## Methods

Following Malinin and Gales 2021, we evaluate different error measures to use for selective prediction based on the Predictive Rejection Ratio (PRR). See the "Prediction Rejection Ratio" section in the Appendix for details on this metric.

### Automatic Speech Recognition

We use the LibriSpeech dataset for training an ASR model. The dataset has the following splits:

| Split | No. examples |
| ----- | ------------ |
| train-clean-100 |  28540 |
| train-clean-360 | 104015 |
| train-other-500 | 148689 |
| dev-clean | 2704 |
| dev-other | 2865 |
| test-clean | 2621 |
| test-other | 2940 |

100, 360, and 500 are the number of hours. The split of examples by the number of hours is just for downloading convenience. The "clean" split is supposed to contain higher quality recordings and accents closer to U.S. English than the "other" split.[^1]

For evaluation, we use the following datasets:

| Dataset | Description | No. examples | Mean WER |
| ------- | ----------- | ------------ | -------- |
| LibriSpeech test-clean (LTC) | Audiobooks read by speakers with lower WER from a baseline model | 2620 | 0.0416 |
| LibriSpeech test-other (LTO) | Audiobooks read by speakers with higher WER from a baseline model | 2939 | 0.1021 |
| TED-LIUM (TED) | English language TED talks | 1155 | 0.2328 |

We selected datasets from [torchaudio.datasets](https://pytorch.org/audio/stable/datasets.html), because they were easy to import and process.

We train a 31M parameter ASR "s2t_transformer_s" model on all the train splits (including "train-other-500") following the steps [here](https://github.com/facebookresearch/fairseq/blob/main/examples/speech_to_text/docs/librispeech_example.md). We use the average of the last 10 checkpoints for generation. We use the sequence with the greatest mean token log probability among the final beam search candidates with a beam size of 20 as the predicted transcription.

Our methodology roughly follows Malinin and Gales 2021. They trained models with a similar architecture on the same dataset. However, the models they use are about 10x larger.[^2] They use an ensemble of models trained with different random initializations in their primary analysis, but they show in a secondary analysis that using an ensemble of model checkpoints does not substantively affect their conclusions. They also evaluate on LibriSpeech test-clean and LibriSpeech test-other, but they use the AMI meeting corpus dataset instead of TED as their out-of-domain dataset. We found processing the AMI meeting corpus dataset to be more involved, so we did not use it.

### Machine translation

For the MT task, we use a 270M parameter transformer model from Facebook's submission to the WMT 2019 Translation Task ([Ng et al 2019](https://arxiv.org/abs/1907.06616)) downloaded from [HuggingFace](https://huggingface.co/facebook/wmt19-en-de). For evaluation, we use the following dataset:

| Dataset | Description | No. examples | BLEU |
| ------- | ----------- | ------------ | ---- |
| newstest2020 (WMT) | English-to-German test set for the WMT 2020 Translation Task | 1418 | 0.3685 |

We use the sequence with the greatest mean token log probability among the final beam search candidates with a beam size of 5 as the predicted translation.

Again, our methodology roughly follows Malinin and Gales 2021. They trained models with a similar architecture with a roughly similar number of parameters. However, they used an ensemble of models for their primary analysis, evaluated on newstest2014 instead of newstest2020 and also included an English-to-French translation task.

## Results

Below are the results for the baseline methods using the PRR as the evaluation metric. We find that directly estimating the prediction error (WER for ASR and BLEU for MT) using the samples as substitute references outperforms the joint-sequence, length-normalized entropy from importance weighting beam search (the best performing method in Malinin and Gales 2021). Note that the nucleus sampling hyperparameter is not fine-tuned. We picked 0.9 as an arbitrary, high value less than 1. Highest scores are bolded and next highest scores are italicized.

| Method | LTC | LTO | TED | WMT |
| ------ | --- | --- | --- | --- |
| Joint-sequence, length-normalized entropy from importance weighting beam search with beam of 20 (Best performing method in Malinin and Gales 2021) | *0.7042* | *0.7279* | 0.6794 | 0.2874 |
| Joint-sequence, length normalized entropy from 100 ancestral samples | 0.6497 | 0.6517 | 0.5419 | 0.1136 |
| Joint-sequence, length normalized entropy from 100 nucleus samples (p=0.9) | 0.699 | 0.7215 | 0.6496 | 0.2224 |
| Average word error rate for ASR or negative BLEU for MT between hypothesis and 100 ancestral samples | 0.5818 | 0.6671 | **0.7238** | 0.2000 |
| Average word error rate for ASR or negative BLEU for MT between hypothesis and 100 nucleus samples (p=0.9) | **0.7061** | **0.7468** | *0.7187* | **0.3310** |
| Negative mean of the token probabilities of the predicted transcription| 0.7015 | 0.7263 | 0.6701 | 0.2914 |
| Negative sum of the token probabilities of the predicted transcription | 0.2964 | 0.3465 | 0.1697 | 0.0604 |

## Appendix

### Prediction Rejection Ratio

We evaluate selective prediction using the Prediction Rejection Ratio (PRR). The PRR is computed by first plotting the "Prediction Rejection Curves". The x-axis of the plot is the proportion of predicted sequences rejected from 0% to 100%. And the y-axis is the average quality of the predicted sequences having rejected x% of those sequences and replaced them with their corresponding ground-truth, reference sequences. A predicted sequence is replaced with its reference sequence in the order of a given confidence score from lowest confidence to highest. An oracle confidence score is just the quality of the predicted sequence as compared to the reference sequence (e.g., the WER of the predicted transcription compared to the reference transcription). A random confidence score just assigns a random number to each sequence. The PRR is the ratio of the area between the Prediction Rejection Curve for the random confidence score and the given confidence score to the area between the Prediction Rejection Curve for the random confidence score and the oracle confidence score.

The figure below shows the different areas involved in the calculation with quality defined as classification error:

![prediction_rejection_curves](/img/prediction_rejection_curves.png)

See "5.2 Evaluation Metrics", Pg. 96 in [Malinin 2019](http://mi.eng.cam.ac.uk/~mjfg/thesis_am969.pdf) for a more detailed explanation.

## Footnotes

[^1]: The split of "clean" vs "other" is described as follows: "A simple automatic procedure was used to select the audio in the first two sets to be, on average, of higher recording quality and with accents closer to US English. An acoustic model was trained on WSJ's si-84 data subset and was used to recognize the audio in the corpus, using a bigram LM estimated on the text of the respective books. We computed the Word Error Rate (WER) of this automatic transcript relative to our reference transcripts obtained from the book texts. The speakers in the corpus were ranked according to the WER of the WSJ model's transcripts, and were divided roughly in the middle, with the lower-WER speakers designated as "clean" and the higherWER speakers designated as 'other'." ([Panayotov et al 2015](http://www.danielpovey.com/files/2015_icassp_librispeech.pdf).

[^2]: Malinin and Gales 2021 cite [Mohamed et al 2020](https://arxiv.org/pdf/1904.11660.pdf), which describes their canonical model as having 223M parameters.
