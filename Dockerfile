FROM python:3.9

# වැඩ කරන තැන හදමු
WORKDIR /code

# Git ඉන්ස්ටෝල් කරමු
RUN apt-get update && apt-get install -y git

# GitHub Repo එක clone කරමු
RUN git clone https://github.com/Iroshanapragith120/lokeshanweb.git .

# දැන් requirements ඉන්ස්ටෝල් කරමු (දැන් ෆයිල් එක තියෙන නිසා එරර් එන්නේ නැහැ)
RUN pip install --no-cache-dir -r requirements.txt

# Permissions හදමු
RUN chmod -R 777 /code

# පෝට් එක 7860 ම වෙන්න ඕනේ
EXPOSE 7860

CMD ["python", "app.py"]
