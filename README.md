# Stable-and-Personalised-Lexical-Profiles
Code for TSD Conference paper 2025: Towards Stable and Personalised Profiles for Lexical Alignment in Spoken Human-Agent Dialogue

This repository contains resources for the paper:

**Towards Stable and Personalised Profiles for Lexical Alignment in Spoken Human-Agent Dialogue**
by Keara Schaaij, Roel Boumans, Tibor Bosse, and Iris Hendrickx 

## Data

The spoken dialogue transcripts used for constructing lexical profiles in in this study are subject to access and usage restrictions imposed by the data providers and therefore cannot be shared publicly. 
Researchers that want to reproduce the experiments or reuse (part of) the code must obtain the transcripts from the original sources and ensure compliance with the relevant terms of use from the provider.

**Data source**

Nederlands Veteraneninstituut (NLVI): Interviewcollectie Nederlandse veteranen (ICNV) (2024). https://www.veteranenvertellen.nl/

The following interview ID's from the ICNV collection were used in this study:

[243, 349, 436, 451, 566, 596, 597, 602, 605, 606, 611, 616, 716, 750, 781, 789, 797, 798, 804, 815, 852, 966, 967, 968, 973, 1016, 1026, 1063, 1083, 1106, 1125, 1297, 1299, 1300, 1301, 1302, 1323, 1324, 1413, 1444, 1445, 1463, 1487, 1551, 1630, 1650, 1651, 1668, 1672, 1700]. The _metadata_ICNV.csv_ contains additional information for these transcripts including gender of the speaker and duration of the interview. 

## Citation

If you want to use this work, please cite as: 

```bibtex
@InProceedings{10.1007/978-3-032-02548-7_5,
author="Schaaij, Keara
and Boumans, Roel
and Bosse, Tibor
and Hendrickx, Iris",
editor="Ek{\v{s}}tein, Kamil
and Konop{\'i}k, Miloslav
and Pra{\v{z}}{\'a}k, Ond{\v{r}}ej
and P{\'a}rtl, Franti{\v{s}}ek",
title="Towards Stable and Personalised Profiles for Lexical Alignment in Spoken Human-Agent Dialogue",
booktitle="Text, Speech, and Dialogue",
year="2026",
publisher="Springer Nature Switzerland",
address="Cham",
pages="48--59",
abstract="Lexical alignment, where speakers start to use similar words across conversation, is known to contribute to successful communication. However, its implementation in conversational agents remains underexplored, particularly considering the recent advancements in large language models (LLMs). As a first step towards enabling lexical alignment in human-agent dialogue, this study draws on strategies for personalising conversational agents and investigates the construction of stable, personalised lexical profiles as a basis for lexical alignment. Specifically, we varied the amounts of transcribed spoken data used for construction as well as the number of items included in the profiles per part-of-speech (POS) category and evaluated profile performance across time using recall, coverage, and cosine similarity metrics. It was shown that smaller and more compact profiles, created after 10 min of transcribed speech containing 5 items for adjectives, 5 items for conjunctions, and 10 items for adverbs, nouns, pronouns, and verbs each, offered the best balance in both performance and data efficiency. In conclusion, this study offers practical insights into constructing stable, personalised lexical profiles, taking into account minimal data requirements, serving as a foundational step toward lexical alignment strategies in conversational agents.",
isbn="978-3-032-02548-7"
}
```


## Acknowledgments
This work is part of the project Responsible AI for Voice Diagnostics (RAIVD) with file number NGF.1607.22.013 of the research program NGF AiNed Fellowship Grants, which is financed by the Dutch Research Council (NWO).

