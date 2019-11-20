# BERT’s Syntax (copy)




----------




## Take aways (up-to-date 5.11.2019)


1. There are specilized heads in BERT model, that find syntactic relations. 
2. Discovered relation may diverge from whtat is provided in guidelines. For instance there are different from Universal Dependencies for english.
3. Averaging of multiple heads or each relation improves the results.






----------


## Attachment Score Results

Results for the best configuration for each dependency relation. English development set 

                        
| Relation            | Direction        | Accuracy (best head) | Accuracy (selected heads averaged) | Positional baseline |
| ------------------- | ---------------- | -------------------- | ---------------------------------- | ------------------- |
| nominal subject     | head → dependent | 62.8%                | **79.1%**                          | 49.2%               |
| object              | dependent → head | 76.5%                | **82.7%**                          | 41.4%               |
| adjective modifier  | dependent → head | 80.8%                | **83.9%**                          | 76.3%               |
| adverb modifier     | dependent → head | 48.2%                | **58.1%**                          | 45.7%               |
| noun modifier       | head → dependent | 41.0%                | **62.0%**                          | 37.5%               |
| numerical modiffier | dependent → head | 60.7%                | **70.9%**                          | 55.6%               |
| compound            | head → dependent | 78.4%                | 84.2%                              | **84.7%**           |
| determiner          | dependent → head | 87.1%                | **89.6%**                          | 58.4%               |
| auxiliary           | dependent → head | 83.5%                | **86.7%**                          | 60.1%               |
| adjective clause    | head → dependent | 36.8%                | **50.2%**                          | 35.2%               |
| adverbial clause    | dependent → head | 20.2%                | **24.9%**                          | 11.3%               |
| subject clause      | head → dependent | 73.7%                | **81.6%**                          | 28.9%               |



----------


## Subject Heads


![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572880563495_image.png)




    
    those who are competent among us and responsible enough to solve their own problems are , we believe , the people themselves .



![Gold annotation and graph derived from selected attention heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572880823025_image.png)




----------


## Object Heads




![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572879904784_image.png)




----------



## Adjective Modifier Head


![Avaraged attention of selected subject heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572881243629_image.png)




    croatia has set an example in the region , in terms of both its political and its economic development since the end of the yugoslav wars .



![Gold annotation and graph derived from selected attention heads](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572881406034_image.png)




----------





## Differences from Universal Dependencies for English
    1. instead copula relation we treat `to be` as predicate of a sentence E. g. `He is a runner`
    2. `exlpletive`  relations are treated as `subject`. E.g. in sentence `There are many ways` “There” will be treated as subject.
    3. Predicate → Subject is more often retived than Subject → Predicate.








----------


## Check best head accuracy in test set



![Europarl dev english](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572872556865_uas-subject-p2d.png)




![Europarl test english](https://paper-attachments.dropbox.com/s_2FAE1A8FDC5A9D836062ABC6ECDF4249FAED6D9D6668416C2B5646DABB1C4337_1572872593703_uas-subject-p2d.png)






----------



## Ideas 💡 


1. Probabilistic instead of “hard” dependency relations obtained. Should be benefitial for use in strucure aware models.
2. Apart from head selection gold annotation is not used.  Error analysis could reveal some drawbacks of the base annotation.
3. With multilingual BERT the analysis can be repeated for other languages even with scarce annotated corpus.


----------



![](http://media.giphy.com/media/LoGh1t5iGxFOE/giphy.gif)



