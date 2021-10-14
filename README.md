1. python restart_Tendermint.py
2. In a second terminal run~ python app.py
3. In a third terminal run~ python client.py upload {"string"}
4. In the same terminal we can query about all the uploaded files with their respective file-ids~~ python client.py query
5. Same terminal, after file is uploaded, approvers run~ python client.py query --file-id "paste the file-id", this represents the k approvers chosen randomly out of n
6. The approvers give their reviews~ python client.py approve --id A1 "file-id"
7. After the k reviewers give their reviews the Majority chosen review is added using True(if approved)/False(if disapproved)
