# TeleMom_reproducibility
This is a code replication of the conference paper TeleMoM: Consensus-Driven Telecom Intelligence via Mixture of Models(see the link for detailshttps://arxiv.org/abs/2504.02712). The authors have not released the official code, and I have only implemented a very basic version by calling various large language model APIs without fine-tuning any of the models.

During runtime, the model also needs to be downloaded from the provided link into the modelsdirectory.(https://huggingface.co/google-bert/bert-base-chinese/tree/main)

The code still has many issues, such as saving results to JSON files, encapsulating functions for reuse, and enabling parallel batch processing.

Optimizations may be made to the code in the future.

Depending on our laboratory's needs, we may develop an intelligent agent for mobile communication threat detection based on this work. Please stay tuned for updates.

