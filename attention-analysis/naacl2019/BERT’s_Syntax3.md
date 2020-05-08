# BERT’s Syntax




----------




## Take aways (20.11.2019)


1. There are specilized heads in BERT model, that find syntactic relations. 
2. Discovered relation may diverge from whtat is provided in guidelines. For instance there are different from Universal Dependencies for english.
3. Averaging of multiple heads or each relation improves the results.






----------


## Attachment Score Results

Results for the best configuration for each dependency relation. English development set 

                        
| Relation            | Direction        | Attention<br>best head | Attention heads av. | Attention<br>heads av.<br>POS | Positional baseline | Positional<br>baseline<br>POS |
| ------------------- | ---------------- | ---------------------- | ------------------- | ----------------------------- | ------------------- | ----------------------------- |
| adjective clause    | head → dependent | 36.8%                  | 50.2%               | **90.1%**                     | 35.2%               | 67.0%                         |
| adjective modifier  | dependent → head | 80.8%                  | 83.9%               | **93.1%**                     | 76.3%               | 87.8%                         |
| adverb modifier     | dependent → head | 48.2%                  | 58.1%               | **83.2%***                    | 45.7%               | 75.1%                         |
| adverbial clause    | dependent → head | 20.2%                  | 24.9%               | **64.9%***                    | 11.3%               | 56.0%                         |
| auxiliary           | dependent → head | 83.5%                  | 86.7%               | **98.7%**                     | 60.1%               | 98.0%                         |
| compound            | head → dependent | 78.4%                  | 84.2%               | **93.4%***                    | 84.7%               | 90.2%                         |
| determiner          | dependent → head | 87.1%                  | 89.6%               | **99.1%***                    | 58.4%               | 88.7%                         |
| nominal subject     | head → dependent | 62.8%                  | 79.1%               | **90.4%***                    | 49.2%               | 82.4%                         |
| noun modifier       | head → dependent | 41.0%                  | 62.0%               | **83.0%***                    | 37.5%               | 81.1%                         |
| numerical modiffier | dependent → head | 60.7%                  | 70.9%               | **92.6%***                    | 55.6%               | 82.2%                         |
| object              | dependent → head | 76.5%                  | 82.7%               | **95.4%**                     | 41.4%               | 93.7%                         |
| subject clause      | head → dependent | 73.7%                  | 81.6%               | **97.4%***                    | 28.9%               | 86.8%                         |

*- direction changed


----------


## Syntactic Tree Construction


| Metric | Attention + POS<br>1000 sents seen | Attention + POS<br>10 sents seen |
| ------ | ---------------------------------- | -------------------------------- |
| UAS    | 66.47%                             | 50.79%                           |
| LAS    | 38.95%                             | 17.87%                           |

-26.1 % correlation between UAS and token number.


----------



    the beneficiaries have already been traumatised by the break with the culture and traditions of the country they come from .
![Silver annotation and created syntactic graph](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1574248799075_image.png)




----------
## Subject Heads (head → dependent)


![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572880563495_image.png)

    those who are competent among us and responsible enough to solve their own problems are , we believe , the people themselves .
![Gold annotation and graph from selected attention heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572880823025_image.png)

----------
## Object Heads (dependent → head)


![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572879904784_image.png)

----------
## Adjective Modifier Head (dependent → head)
![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572881243629_image.png)

    croatia has set an example in the region , in terms of both its political and its economic development since the end of the yugoslav wars .


![Gold annotation and graph from selected attention heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572881406034_image.png)

----------







## Differences from Universal Dependencies for English
    1. instead copula relation we treat `to be` as predicate of a sentence E. g. `He is a runner`
    2. `expletive`  relations are treated as `subject`. E.g. in sentence `There are many ways` “There” will be treated as subject.
    3. ~~Predicate → Subject is more often retrieved than Subject → Predicate.~~









----------


## Ideas 💡 


1. Probabilistic instead of “hard” dependency relations obtained. Should be beneficial for use in structure aware models.
2. ~~Apart from head selection gold annotation is not used.  Error analysis could reveal some drawbacks of the base annotation.~~
3. With multilingual BERT the analysis can be repeated for other languages even with scarce annotated corpus.


----------
## Less supervision
1. Select heads by non syntactic features, e.g.:
    1. variability
    2. attention concentration below/above diagonal
    3. attention distance from a diagonal
2. Substitute POS information. EM optimization:
    
    $$\displaystyle\prod_{X\to Y}{P(Y=y_{dep}|X=x_{dep})P(X\to Y|Y=y_{dep})} \cdot P(X_{ROOT}=root)$$
    
----------
## Multilingual results:


https://docs.google.com/spreadsheets/d/1Qx8Efat9OCusbjMm30axzCVcQ2TRFFwDlXqw67y7qf4/edit?usp=sharing


[https://docs.google.com/spreadsheets/d/1Qx8Efat9OCusbjMm30axzCVcQ2TRFFwDlXqw67y7qf4/edit](https://docs.google.com/spreadsheets/d/1Qx8Efat9OCusbjMm30axzCVcQ2TRFFwDlXqw67y7qf4/edit)

Similar heads have the same function for many languages in multilingual Bert.

----------



![](http://media.giphy.com/media/LoGh1t5iGxFOE/giphy.gif)


