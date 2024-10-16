# -- coding: utf-8 --
"""
Created on Thu Sep 26 05:31:49 2024

@author: CITD
"""



##########

from transformers import T5Tokenizer, T5ForConditionalGeneration #importing the pre-trained model
from sklearn.model_selection import train_test_split #splitting the data into test and training

##########

#pairing up the data
import os #importing operating system library to read files

# Paths to your folders
# Paths to your folders
text_folder1 = "C:/Users/CITD/Desktop/T5 Training folder/training articles" #Article dataset path

summary_folder = "C:/Users/CITD/Desktop/T5 Training folder/training summary" #Summary dataset path

# Function to load text files and summaries
def load_texts_and_summaries(text_folder, summary_folder): #Function to load data
    data = []
    
    # Get list of text files
    text_files = sorted(os.listdir(text_folder)) #accessing the directories and sorting all the Article files by alphabetical order (or by the mentioned sorting parameter) and stores it in the form of text files
    summary_files = sorted(os.listdir(summary_folder)) #Listing and sorting summary files
    
    for text_file, summary_file in zip(text_files, summary_files): #zip creates a tuple in which one file from the articles is paired with one file from summary folder in respective order. if the length of two folders are unequal then the zip stops when the shorter folder ends
        # Ensure the file names match or follow a known pattern
        if text_file.split('.')[0] == summary_file.split('.')[0]: 
            with open(os.path.join(text_folder, text_file), 'r', encoding='utf-8') as tf:
                text = tf.read()
            with open(os.path.join(summary_folder, summary_file), 'r', encoding='utf-8') as sf:
                summary = sf.read()
            
            data.append({'text': text, 'summary': summary})
    
    return data

# Load the data
dataset = load_texts_and_summaries(text_folder1, summary_folder)

##########
#%%
from transformers import T5Tokenizer, T5ForConditionalGeneration
tokenizer = T5Tokenizer.from_pretrained('t5-base')
model = T5ForConditionalGeneration.from_pretrained('t5-base')

##########

import pandas as pd
# Convert the data into a Hugging Face dataset
dataset = pd.DataFrame(dataset)
print(dataset)
train_df, test_df = train_test_split(dataset, test_size=0.2, random_state=42)
#%%
##########

#pip uninstall keras keras-nightly keras-2 keras-preprocessing
#pip uninstall tensorflow
#pip install tensorflow==2.11 keras==2.11

########

from transformers import Trainer, TrainingArguments

# Define the training arguments
training_args = TrainingArguments(
    output_dir="C:/Users/CITD/Desktop/BBC News Summary/News Articles/business/result",          # Output directory
    evaluation_strategy="epoch",     # Evaluate at the end of each epoch
    learning_rate=5e-5,              # Learning rate
    #per_device_train_batch_size=8,   # Batch size for training
    #per_device_eval_batch_size=8,    # Batch size for evaluation
    num_train_epochs=3,              # Number of epochs
    weight_decay=0.01,               # Weight decay
    save_total_limit=3,              # Save up to 3 model checkpoints
)


import torch
from torch.utils.data import Dataset

class T5Dataset(Dataset):
    def _init_(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.dataframe = dataframe
        self.max_len = max_len

    def _len_(self):
        return len(self.dataframe)

    def _getitem_(self, index):
        row = self.dataframe.iloc[index]  # Use iloc to access by index
        text = row['text']
        summary = row['summary']

        # Tokenization
        input_encoding = self.tokenizer.encode_plus(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        target_encoding = self.tokenizer.encode_plus(
            summary,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': input_encoding['input_ids'].flatten(),
            'attention_mask': input_encoding['attention_mask'].flatten(),
            'labels': target_encoding['input_ids'].flatten()
        }

max_len=128
train_dataset = T5Dataset(train_df, tokenizer, max_len)
test_dataset = T5Dataset(test_df, tokenizer, max_len)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Fine-tune the model
trainer.train()
#%%
results=trainer.evaluate()

model.save_pretrained("C:/Users/CITD/Desktop/T5 Training folder/Trained_Model" )

tokenizer.save_pretrained("C:/Users/CITD/Desktop/T5 Training folder/Trained_Model" )



#%%
############

from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load the fine-tuned model and tokenizer
tokenizer = T5Tokenizer.from_pretrained('C:/Users/CITD/Desktop/BBC News Summary/fine-tunedT5/fine-tunedT5')
model = T5ForConditionalGeneration.from_pretrained('C:/Users/CITD/Desktop/BBC News Summary/fine-tunedT5/fine-tunedT5')

# Summarize new text
input_text = """
Apple laptop is 'greatest gadget'

The Apple Powerbook 100 has been chosen as the greatest gadget of all time, by US magazine Mobile PC.

The 1991 laptop was chosen because it was one of the first "lightweight" portable computers and helped define the layout of all future notebook PCs. The magazine has compiled an all-time top 100 list of gadgets, which includes the Sony Walkman at number three and the 1956 Zenith remote control at two. Gadgets needed moving parts and/or electronics to warrant inclusion. The magazine specified that gadgets also needed to be a "self-contained apparatus that can be used on its own, not a subset of another device".

"In general we included only items that were potentially mobile," said the magazine.

"In the end, we tried to get to the heart of what really makes a gadget a gadget," it concluded. The oldest "gadget" in the top 100 is the abacus, which the magazine dates at 190 A.D., and put in 60th place. Other pre-electronic gadgets in the top 100 include the sextant from 1731 (59th position), the marine chronometer from 1761 (42nd position) and the Kodak Brownie camera from 1900 (28th position). The Tivo personal video recorder is the newest device to make the top 10, which also includes the first flash mp3 player (Diamound Multimedia), as well as the first "successful" digital camera (Casio QV-10) and mobile phone (Motorola Startac). The most popular gadget of the moment, the Apple iPod, is at number 12 in the list while the first Sony transistor radio is at number 13.

Sony's third entry in the top 20 is the CDP-101 CD player from 1983. "Who can forget the crystalline, hiss-free blast of Madonna's Like A Virgin emenating from their first CD player?" asked the magazine. Karl Elsener's knife, the Swiss Army Knife from 1891, is at number 20 in the list. Gadgets which could be said to feature surprisngly low down in the list include the original telephone (23rd), the Nintendo GameBoy (25th), and the Pulsar quartz digital watch (36th). The list also contains plenty of oddities: the Pez sweet dispenser (98th), 1980s toy Tamagotchi (86th) and the bizarre Ronco inside the shell egg scrambler (84th).

Why worry about mobile phones. Soon they will be subsumed into the PDA's / laptops etc.

What about the Marine Chronometer? Completely revolutionised navigation for boats and was in use for centuries. For it's time, a technological marvel!

Sony Net Minidisc! It paved the way for more mp3 player to explode onto the market. I always used my NetMD, and could not go anywhere without it.

A laptop computer is not a gadget! It's a working tool!

The Sinclair Executive was the world's first pocket calculator. I think this should be there as well.

How about the clockwork radio? Or GPS? Or a pocket calculator? All these things are useful to real people, not just PC magazine editors.

Are the people who created this list insane ? Surely the most important gadget of the modern age is the mobile phone? It has revolutionalised communication, which is more than can be said for a niche market laptop. From outside the modern age, the marine chronometer is the single most important gadget, without which modern transportation systems would not have evolved so quickly.

Has everyone forgot about the Breville pie maker??

An interesting list. Of the electronic gadgets, thousands of journalists in the early 1980s blessed the original noteboook pc - the Tandy 100. The size of A4 paper and light, three weeks on a set of batteries, an excellent keyboard, a modem. A pity Tandy did not make it DOS compatible.

What's an Apple Powerbook 100 ? It's out of date - not much of a "gadget". Surely it has to be something simple / timeless - the tin opener, Swiss Army Knife, safety razor blade, wristwatch or the thing for taking stones out of horses hooves ?

It has to be the mobile phone. No other single device has had such an effect on our way of living in such a short space of time.

The ball point pen has got to be one of the most used and common gadgets ever. Also many might be grateful for the pocket calculator which was a great improvement over the slide rule.

The Casio pocket calculator that played a simple game and made tinny noises was also a hot gadget in 1980. A true gadget, it could be carried around and shown off.

All top 10 are electronic toys, so the list is probably a better reflection of the current high-tech obsession than anyhting else. I say this as the Swiss Army Knife only made No 20.

Sinclair QL a machine far ahead of its time. The first home machine with a true multi-takings OS. Shame the marketing was so bad!!!

Apple.. a triumph of fashion over... well everything else.

Utter rubbish. Yes, the Apple laptop and Sony Walkman are classic gadgets. But to call the sextant and the marine chronometer 'gadgets' and rank them as less important than a TV remote control reveals a quite shocking lack of historical perspective. The former literally helped change the world by vastly improving navigation at see. The latter is the seed around which the couch potato culture has developed. No competition.

I'd also put Apple's Newton and the first Palm Pilot there as the front runners for portable computing, and possibly the Toshiba Libretto for the same reason. I only wish that Vulcan Inc's Flipstart wasn't just vapourware otherwise it would be at the top.

How did a laptop ever manage to beat off the challenge of the wristwatch or the telephone (mobile or otherwise)? What about radios and TVs?

The swiss army knife. By far the most useful gadget. I got mine 12 years ago. Still wearing and using it a lot! It stood the test of time.

Psion Organiser series 3, should be up there. Had a usable qwerty keyboard, removable storage, good set of apps and programmable. Case design was good (batteries in the hinge - a first, I think). Great product innovation.

The first mobile PC was voted best gadget by readers of...err... mobile PC?! Why do you keep putting these obviously biased lists on your site? It's obviously the mobile phone or remote control, and readers of a less partisan publication would tell you that.

The Motorola Startac should be Number One. Why? There will be mobile phones long after notebook computers and other gadgets are either gone or integrated in communications devices.

The Psion series 3c! The first most practical way to carry all your info around...

I too would back the Sinclair Spectrum - without this little beauty I would never have moved into the world of IT and earn the living that I do now.

I'd have put the mobile phone high up the list. Probably a Nokia model.

Sinclair Spectrum - 16k. It plugged into the tv. Games were rubbish but it gave me a taste for programming and that's what I do for a living now.

I wish more modern notebooks -- even Apple's newest offerings -- were more like the PB100. Particularly disheartening is the demise of the trackball, which has given way to the largely useless "trackpad" which every notebook on the market today uses. They're invariably inaccurate, uncomfortable, and cumbersome to use.

Congratulations to Apple, a deserved win!
"""
input_ids = tokenizer.encode("summarize: " + input_text, return_tensors="pt", max_length=512, truncation=True)

# Generate the summary
summary_ids = model.generate(input_ids, max_length=700, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

print(summary)