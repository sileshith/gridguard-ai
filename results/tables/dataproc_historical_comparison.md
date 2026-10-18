# Historical vs fresh manual Dataproc validation

| model | metric | historical | fresh | signed_difference | absolute_difference | classification |
|---|---|---|---|---|---|---|
| lr | PR_AUC | 0.8542 | 0.8554999165 | 0.0012999165000000534 | 0.0012999165000000534 | close reproduction |
| lr | ROC_AUC | 0.9699 | 0.9699829715 | 8.297150000002862e-05 | 8.297150000002862e-05 | close reproduction |
| lr | precision | 0.8264 | 0.8313113413 | 0.004911341299999927 | 0.004911341299999927 | close reproduction |
| lr | recall | 0.6918 | 0.6875810361 | -0.0042189638999999834 | 0.0042189638999999834 | close reproduction |
| lr | F1 | 0.7531 | 0.7526457067 | -0.00045429330000001933 | 0.00045429330000001933 | close reproduction |
| rf | PR_AUC | 0.8736 | 0.8683321235 | -0.005267876500000046 | 0.005267876500000046 | meaningful discrepancy |
| rf | ROC_AUC | 0.9663 | 0.9656576838 | -0.0006423161999999927 | 0.0006423161999999927 | meaningful discrepancy |
| rf | precision | 0.9234 | 0.8784405399 | -0.04495946009999996 | 0.04495946009999996 | meaningful discrepancy |
| rf | recall | 0.6585 | 0.6566886521 | -0.0018113478999999266 | 0.0018113478999999266 | meaningful discrepancy |
| rf | F1 | 0.7687 | 0.7515483871 | -0.0171516129 | 0.0171516129 | meaningful discrepancy |
| gbt | PR_AUC | 0.9262 | 0.9249987208 | -0.001201279200000016 | 0.001201279200000016 | close reproduction |
| gbt | ROC_AUC | 0.9832 | 0.9824823161 | -0.0007176838999999324 | 0.0007176838999999324 | close reproduction |
| gbt | precision | 0.9256 | 0.9259778401 | 0.0003778400999999709 | 0.0003778400999999709 | close reproduction |
| gbt | recall | 0.7829 | 0.782062123 | -0.0008378770000000424 | 0.0008378770000000424 | close reproduction |
| gbt | F1 | 0.8483 | 0.8479569695 | -0.0003430305000000633 | 0.0003430305000000633 | close reproduction |


User-supplied manually verified cloud results. Historical values are rounded. Raw cloud JSON was not locally reviewed during this integration.
