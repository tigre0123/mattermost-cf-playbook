# cloudformationを使う場合
```Bash
aws cloudformation deploy \
    --template-file ansible-cf-mattermost.yml \
    --stack-name mattermost \
    --capabilities CAPABILITY_NAMED_IAM
```
# インスタンスにansibleを実行するだけの場合（デバッグ用）
Todo:Dockerを使うようにする。そうすればwindows,macで同じように使えるようになるだろう<br>

windowsで動かす方法がわからなかったのでWSLにインストールすることにした。
https://qiita.com/Tkm08/items/58e1fb7990387a2e9c76
https://docs.ansible.com/ansible/2.9_ja/user_guide/windows_faq.html
準備作業
```
sudo apt-get update
sudo apt-get install python3-pip git libffi-dev libssl-dev -y
sudo pip install ansible pywinrm
ansible-playbook --version

mkdir ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
```
これで準備完了

```Bash
cd mattermost-cf-playbook

# サーバ設定(public dns)
vi host_vars/prod.yml

# ansible実行
ansible-playbook -i host_vars/prod.yml site.yml

# codeチェック
ansible-lint site.yml
```