# !/bin/zsh

python arxiv_crawler.py
python snapshot.py
d=$(date +%Y-%m-%d.txt)
vi paper/$d