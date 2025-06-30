import json
import logging
import os
import requests
import ollama

def extract_toeic_words_with_ollama(transcript_text):
    """
    使用 Ollama 本地 LLM 進行單字萃取
    transcript_text: 字幕內容
    video_title: 影片標題
    """
    if not transcript_text:
        logging.error("字幕內容為空，無法提取單字")
        return []

    system_prompt = f"""You are a professional English teacher. From the text '{script}', provide 10 distinct vocabulary words.
        For each word, you must provide:
        1.  The word itself.
        2.  Its English definition.
        3.  Its part of speech (e.g., noun, verb, adjective, adverb).
        4.  An example sentence using the word.

        Output your response ONLY as a JSON array of objects. Each object should have the keys: "word", "definition", "part_of_speech", and "example_sentence".
        Do NOT include any other text, explanations, or summaries outside the JSON.

        Here is an example of the desired JSON format:
        [
        {{
            "word": "serene",
            "definition": "calm, peaceful, and untroubled; tranquil.",
            ""part_of_speech": "adjective",
            "example_sentence": "The lake was serene in the early morning, reflecting the clear sky."
        }},
        {{
            "word": "ubiquitous",
            "definition": "present, appearing, or found everywhere.",
            "part_of_speech": "adjective",
            "example_sentence": "Smartphones have become ubiquitous in modern society."
        }}
        ]
        """

    # OLLAMA_CHAT_API_URL = os.getenv('OLLAMA_CHAT_API_URL', 'http://localhost:11434/api/generate')
    # MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'gemma')
    messages = [
        {"role": "system", "content": system_prompt},
        # {"role": "user", "content": user_prompt}
    ]
    options = {
        # "num_predict": 8192,
        "temperature": 0,
        # "top_p": 0.95,
    }

    try:
        response = ollama.chat(model='gemma3', messages=messages, options=options)
        print(response['message']['content'])
        response_message = response['message']['content']

        # response 預處理，避免模型產出除了 json 以外的內容造成無法成功轉換成 json 格式
        response_message = response_message.strip() # 先用 strip() 移除可能的空白符
        if response_message.startswith("```json"):
            response_message = response_message[len("```json"):].lstrip('\n') # 移除開頭標記和可能的換行符
        if response_message.endswith("```"):
            response_message = response_message[:-len("```")].rstrip('\n') # 移除結尾標記和可能的換行符
        
        # 嘗試解析 JSON
        try:
            print(response_message)
            words_data = json.loads(response_message)
            logging.info(f"成功提取 {len(words_data[0])} 個單字 (Ollama)")
            # print(words_data['words'])
            return words_data
        except Exception as e:
            logging.error(f"Ollama 回傳內容無法解析為 JSON: {e}")
            return []
    except Exception as e:
        logging.error(f"使用 Ollama 提取單字時發生錯誤: {e}")
        return []

def generate_toeic_quiz(gemini_model, words):
    """
    根據提取的單字生成 TOEIC 考題
    
    Args:
        gemini_model: Gemini 模型實例
        words: 單字列表，每個單字包含 word, chinese, part_of_speech, example
        
    Returns:
        包含50題考題的列表
    """
    if not words:
        logging.error("沒有單字可以生成考題")
        return []
        
    prompt = f"""
    請根據以下單字列表生成50題 TOEIC 考試風格的選擇題。
    每個題目應該包含：
    1. 題目（使用單字或其變化形式）
    2. 4個選項（A, B, C, D）
    3. 正確答案
    4. 解釋
    
    單字列表：
    {json.dumps(words, ensure_ascii=False, indent=2)}
    
    請用以下JSON格式回傳：
    {{
        "questions": [
            {{
                "question": "The company's management team has decided to _____ the project due to budget constraints.",
                "options": {{
                    "A": "terminate",
                    "B": "initiate",
                    "C": "celebrate",
                    "D": "decorate"
                }},
                "correct_answer": "A",
                "explanation": "terminate 意為終止，符合句意。其他選項：initiate（開始）、celebrate（慶祝）、decorate（裝飾）都不符合上下文。"
            }}
        ]
    }}
    要求：
    1. 題目要符合 TOEIC 考試的難度和風格
    2. 選項要合理且具有迷惑性
    3. 解釋要清楚說明為什麼是正確答案
    4. 確保生成恰好50題
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        result_text = response.text
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end]
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.rfind("```")
            result_text = result_text[json_start:json_end]
        quiz_data = json.loads(result_text.strip())
        logging.info(f"成功生成 {len(quiz_data['questions'])} 題考題")
        return quiz_data['questions']
    except Exception as e:
        logging.error(f"使用 Gemini 生成考題時發生錯誤: {e}")
        return [] 
    
if __name__ == '__main__':
    script = """I was able to customize my cloud code into a cloud designer which allows me to iterate UI 10 times faster in cursor and wings serve directly forking and generating five to even 10 different UIs at the same time and all this are made possible with some hidden clock code feature like parallel task commands and new SDK that they just introduced. I'll break it down for you so you can replicate on your end. So one thing I think people didn't realize is that you can actually spin up multiple sub agents within cloud code by simply prompiting. For example, I can give a simple prompt. Start a three parallel agent to implement variations of the to-do app UI. And then you will see that it start three different task that is happening at the same time. One agent will be doing minimalist to-do UI. Another will be doing modern to-do and third will be cambban UI. And boom, you just got three totally different style at the same time. So it'll be much faster for you to iterate. And you can imagine we can actually package this to be some really interesting UI iteration process with this parallel task capability. There was actually pretty heated debate last week on Twitter where dev team published a blog post called don't build multi- aent system. One of the key insights they got is that for task like coding where each action you take actually imply specific set of decisions you make and when you do parallel task it is very likely leads to things like merge conflicts because each sub agent has no context about what the other agent is working on and the best approach they found is actually just don't do parallel task at all and putting everything into one single thread. However, a few days later, Entropy released their own blog post about how do they apply multi- aent in their own research system where they build this group of agents and each sub agent can actually have parallel task to do things like research and I think both had pretty valid points because most of the time you do want to making sure the agent has a full context when execute task but there are scenario that makes sense like research it is going to be faster if you spin up five research topics and summarize everything in the end and same thing for the UI design paralas is actually perfect use case because When we do design in Figma, what we often do is that we'll just fork and do a few different variations and compare them kind of side by side and eventually we get like final version. So have that capability of have parallel task on design has been a pretty good pattern and what I want to show you is how I utilize the parallel task capability in cloud code to have some really interesting UI workflow. But before I dive into that, I know many of you are building AI applications or AI agents that needs access to internet data from research about business to get latest news and a smart and reliable way to turn any website data into large language model friendly format is critical. That's why I want to introduce you to FRO. They were the first open- source project. They offer effective way to turn any website into clean format that is optimized for large language model to consume. You can browse through all the subpage of a website and it handle PDF, word doc or even Excel file that are attached from URL and has capability like smart weight d content loading so that you can guess website with more strict anti-bos setup and for the past few months they just launched a whole bunch of new feature that is going to make web scraping 10x easier. For example, they introduced this new search endpoint that's going to give you back the most random websites as well as extract markdown content of those website directly in just one API call. This is going to make your AI application way faster because you don't need scarfolding the whole pipeline of search and scrape from different service. And they also introduced this new extract endpoint where it can handle things like pageionation and page interaction with their own fire one agent that is capable to interact with website like e-commerce to clicks through buttons get a full content and it can even similar complex action like login and authentication as well. All you need is just give a URL, the prompt, the data structure you want and this agent will open up the browser, navigate through the website to multiple different pages until they find information you want. And most importantly, those abilities can be called from API endpoint directly. So you can give your own agents internet and research capability with just few lines code or integrate to automation platform like Zapier and relevance AI by calling firecore API directly. So if you're looking for a smart way to script internet data, I highly recommend you go and check out firecro. Now let's get back how can you customize cloud code into cloud designer. So to understand the workflow I'm going to show you there are four core concepts. We already covered the sub aents part and second one is cloud.md. If you're pretty familiar with cursor is basically cursor rules but for cloud code with this one we can customize how cloud code should work and give it knowledge about what type of task you should do in parallel what type of task you shouldn't. And I will show you a quick example. For example, if you open cloud in any folder and just create a file called cloud.md and you can just put whatever instruction here like you always respond in all caps. Now if you try to run cloud and say hi, it will respond back in all caps. But you can imagine we can also put some very specialized prompt for this as well. For example, this is a prompt that I have been playing with internal UI design where it includes things like the color, font, layout, stuff like that. So I can put in this and also adding maybe some special rules that when you were asked to build UI iterations, you always just create one single HTML file. So I can give a simple prompt like build me a modern to-do app UI. It will basically following my rules. It won't create some complicated project. And this will just create a one single HTML file that contain a nice kind of modern UI. So this is cloud MD the custom rules for cloud code. The next thing which is very powerful called commands. So you can basically predefine list of common workflow that you want cloud to follow. So you can create a folder called cloud. Inside you can have another folder called commands. This is where we're going to create some cool stuff. Let's say you want to create a joke generated command. So you create a joke.md and we can just say make a joke about arguments. So arguments is a special thing that pass to clock in the command so that you almost create a prompt template that can be used for many different scenarios and I can give it some custom instruction always and a joke with a man eating chips and now if I do slash you will see that there's a slash joke option and I will just type in joke then what are you putting down after is what's going to be passed to arguments so I here can say AI coding and then you will see that I generate a prompt about AI coding and with the specific instruction that we give inside here if from cloud code's official doc. It can even do something like you can literally just natural language putting some commands that you wanted to run. It will actually execute those command line before I do the task. For example, you can actually create a command like this where it will do those command line to check get status first before you execute a task. So if I try this and do the joke now it is actually running those command line to check the get status because I didn't set up yet. It's just a not a get repository. But if I initiate the git here and run cloud again, it will give you a different joke about main branch because now I set up the git. So to me this is like a mystery but super super powerful feature. And what I want to show you is how do I use this to create some sort of UI flow. So I'll create another folder inside let's say UI and create a one called extracted system and putting this prompt. Basically it will have the task of the UI it should analyze which we're passing through a image URL and the goal here is to extract like color pattern typography stuff like that and also save the design system JSON into a folder called prd. So this will allow us to give cloud code a kind of UI mock and it will just generate the design system from that. I found that this works much better than you just give the UI reference ask to do right away. And second command I also use is this iterate design MD. So this is the one that I want cloud to spin up three or five sub aents to concurrently implement the same UI in different style. So I will ask it to analyze a design system JSON file we created and then build one single HTML page and output the HTML in the UI iteration folder called UI 1 UI2 UI3. So with these two things I'm going to show you a very interesting workflow. First I will go to website like moen or dribble to just get some UI inspiration. And let's say I quite like this one. I can save this image zui/ extract design system and I will drag this image here and then it will create this design system.json this prd folder as I instructed which have those kind of more detailed style. Next I can call second command iterate design give a prompt a modern phone to-do app using this design style as reference which I'm referring to this design system file we created earlier. Then it will set up three different tasks. You can see for each task it actually has a very detailed task about UI reference design directions like that. By the way, you can use control R to expand and then Ctrl E to see those details. And of course, you can like always toggle between. But honestly, there's still some bugs. So, I'm just going to let it run like this. And now it output three different UI in the UI iterations. If I open them, they all looks somewhat different in terms of style and animations. And what's really cool is that let's assume I like this UI2 version. But I want to iterate a bit further based on this version because I want to build a kind of dark mode and then I can do the same thing again. This iterate UI2 HTML version which is best one so far and try dark mode. Then you will see this time it will analyze the current UI2 design and try to spin up three parallel tasks. And the more I use it, I realized that the way this command line works, it's basically sending a prompt template to the cloud and along with this prompt you put in here. And this is really interesting, right? Because traditionally, if you design software, you probably were uh designing a way that you have to define what type of arguments are and user have to give those arguments. But they basically keep it super free. Uh you just give a free text agent just magically figure out. This is just such interesting kind of design pattern I found. So after 200 seconds, I got three versions of different UI based on the previous version two I like, but some sort of variation between each one of them. Like this one has some kind of glowy uh style, which is pretty cool. But this is kind of the workflow. I can choose the version I like and then ask to iterate a few different versions. I can even probably grab the glowy style from this version as well as a pure dark background from this style. Ask it to iterate. I'm pretty sure it can figure out. And once you done, you can get a HTML that has a style you want. then just start prompting cursor to actually break down into components and build a proper UI in nextJS project. But this workflow of iterating UI is something that I've been trying a lot and it has been really really helpful. But this workflow can only allow you to build like single HTML page. What if you want to set up parallel agent to work on different UI iteration on your actual production NexJS app and this is where the fourth concept comes in Git work tree. So if you're familiar with g most of the time you can only have one branch running on your computer at the same time and g work tree is a feature they have that allow you to set up multiple different sandbox environment of your specific report. So you can get a multiple cloud code each working on a individual work tree without impact each other's work and in the end you can just pick up the version you like and merge them together and all you need to do just run this command get work tree add-b with a branch name and then pass where do you want to copy and create a sandbox of your current rip for example here I have a basic to-do app that I built with nextjs and chass in it has multiple different components it is much more complicated than a single HTML page what I can do is open terminal and do get work tree add b which is branch name and I'll call it like demo branch. Then I'll remove that into a specific folder. Um what I going to do is I will just create a trees folder with the same branch name so it's easier for us to identify and understand what that is about. If I do this you can see a new folder called trees created. Inside it has another folder called demo branch which has everything we have at root branch. So this is how you can set up a work tree. And now I can do cd trees demo branch. And once I get inside, I can do PNPM install and PMP dev. And you will see the same application is running here in a different portal. And the easiest way will be we can just set up a new cloud here and ask it to iterate UI. And once you get one version you're pretty happy with, you can set it up and do get merge demo branch. So this how the work tree works. Theoretically, you can already have a workflow to firstly create multiple different work trees and then set up parallel agents to work on each individual work tree folders. But what I really experimented is I actually created one command called execute parallel agents and this is one command with the prompt template that I have. It will have two steps. First step will be set up multiple different g trees based on the user's request. If a user asks for three different variations then create three different work trees and each one of them follow the naming convention we have and then do pmppm install setup. Then step two is set up parallel sub agents. This is where the master cloud code agent will spin up multiple different sub agents. Each one work on a different branch and this command will basically do the whole workflow for us. Whenever I want multiple different agents to iterate this UI on existing production projects. For the second prompt here, I actually got some inspiration from another content creator called indie dam den who also talk about this parallel agent workflow. So I highly recommend you check out if you want to learn more. But let me quickly show you how does this work. So I have this command that I showed you earlier and just do cloud then I can just slash to use execute parallel agent command and I'll just give a command try three versions of UI one nerdy style one kid style and one gaming style. There we say I will help you create three parallel agents work on different things with three different to-dos. Firstly it will create three work trees for nerdy kit and gaming UI style. Install dependencies in each work tree and then launch three parallel agents to work on each one of them. And now if I open trees you can see there are three different branch and work tree has been created and after that it will start setting up the project. And after setup it's going to launch three parallel agent to implement different UI stuff. And you can see three parallel task has been created. Each one of them going to be assigned to a individual sub agent. And if we do control R you can see the detail of each task that sub agent is receiving. It has the task the prompt the key files to modify and requirements and each task is slightly different to reflect style we want. And this process is going to take some time. I've actually found this is slower than I just call let's say three entropic call in parallel. I assume entropy actually do some kind of re limiting management. So it does take some time but the cool thing is that you get all those UI in one go. So you don't have to follow that specific linear flow and each version will be inside its own folder. So in the end I got three different versions. Each one of the version does look quite different based on the kind of style of prompt it explore like this nerdy dad version this kind of kids version and we also have this kind of gaming style as well. And you can imagine I can even further doing this. Assuming I like this nerdy version, then I can give another parallel task to set up three more new branches to iterate based on this. So this is kind of the workflow I feel like going to be really developed for next few months especially for UI iteration tasks. But in the end just making sure remember to delete the trees that you don't want because each branch actually can be pretty big because you need to install all the packages inside. Meanwhile, I was imagined what if we have this kind of parallel task execution experience plus some sort of easy way for you to set up sandbox, view the results, iterate based on certain design and also delete the work tree when it's not needed. Especially now cloud code has its SDK where we can integrate a coding assistant very easily with custom prompt tools. So during the weekend, my friend Jack and I have been trying this weekend purchase. We basically integrate to cloud AI SDK and build a cursor extension that you can inside your existing pure right away and ask it to start experimenting different UI. You will have Canva on the right side to preview the UI generated. Then select certain version you like and ask it iterated further. So you can visit superdesign.dev and click on install for free button. This will allow you to just one click installing cursor when you serve or any other ID you're using. It will open the superdesign extension and after install you can do command shiftp and this one option called configure entropy API key. So you put your entropy API key here because we are using cloud code SDK behind the scenes and once that part is done click on super design. This will open a chat on the left side and a camera view on the right side and you can give a prompt design me some wireframe of a calculator. Then you will see the agents start working and trigger multiple tasks. Each task with a slightly different uh brief about what type of design it is. You're basically creating design inside the super design design iteration folder. And at this point each design takes roughly 1 minute to generate. They're very clear path for us to optimize and make it way faster. Uh but we just want to ship it as the first version for now. And all the design generated will be showing up on the right side. And now you can see generate a few different kind of wireframe options for the calculator. And once I find the version I prefer, I can click on this which will have a few different options either create a variations or iterate feedback as well as copy prompt for cursor we insert direct with. So I can click on this iterator with feedback button. Then give a prompt. This looks great. Now build a hi-fi mo based on this layout. Then you will see here it generate a few high fidelity mockups based on that specific layout. And you can imagine we can keep iterating giving feedback and once I'm happy I can click on this copy prompt button. This will copy the full style. So you can pass to cursor or cloud code to do the actual implementation of the web app. So this is the first version we spin up going to do a lot of improvements but super keen to just hear feedback. Is this something you find useful? If so, please give it a try. This will be open source project you can just download and try out yourself. So I will put the link in the description below so you can go and try out. Meanwhile, I will put all the problems I shared in AI builder club, which is a community I'm building that has top AI builders who are launching AI products. Myself and other people will share also tips and workflows that we found really useful for both AI coding and build large modelic software. So, I've also put a link in the description below for you to join as well if you want to learn more. I'm really excited about this project and what kind of feedback you guys have. This is just a v 0.01 version that only created one single HTML page. The next version, we're going to add the default work tree support so you can iterate UI of your existing production application. I'll keep you updated. Thank you and I see you next time."""
    extract_toeic_words_with_ollama(script)
#     output = """```json
# [
#   {
#     "word": "iteration",
#     "definition": "The process of repeating a process or task in order to improve it.",
#     "part_of_speech": "noun",
#     "example_sentence": "The software development team used an iterative approach to build the new application."
#   },
#   {
#     "word": "sandbox",
#     "definition": "A controlled environment used for testing or experimentation.",
#     "part_of_speech": "noun",
#     "example_sentence": "The developers created a sandbox to test the new feature without affecting the live system."
#   },
#   {
#     "word": "ubiquitous",
#     "definition": "Existing or being everywhere simultaneously.",
#     "part_of_speech": "adjective",
#     "example_sentence": "Smartphones have become ubiquitous in modern society."
#   },
#   {
#     "word": "workflow",
#     "definition": "A sequence of tasks or operations performed in a specific order.",
#     "part_of_speech": "noun",
#     "example_sentence": "The company implemented a new workflow to streamline the customer service process."
#   },
#   {
#     "word": "iteration",
#     "definition": "The act of repeating a process or task.",
#     "part_of_speech": "verb",
#     "example_sentence": "The designer will iterate on the design based on user feedback."
#   },
#   {
#     "word": "subagents",
#     "definition": "Individual components or entities that work together to achieve a common goal.",
#     "part_of_speech": "noun",
#     "example_sentence": "The complex system relies on a network of subagents to manage data flow."
#   },
#   {
#     "word": "workflow",
#     "definition": "The means by which something is done or accomplished.",
#     "part_of_speech": "verb",
#     "example_sentence": "We need to optimize the workflow to reduce processing time."
#   },
#   {
#     "word": "subagents",
#     "definition": "A smaller, supporting agent or component.",
#     "part_of_speech": "noun",
#     "example_sentence": "The robot uses subagents to perform different tasks."
#   },
#   {
#     "word": "ubiquitous",
#     "definition": "Present, appearing, or existing everywhere.",
#     "part_of_speech": "adjective",
#     "example_sentence": "The internet has become a ubiquitous tool for communication."
#   },
#   {
#     "word": "iteration",
#     "definition": "A single cycle of improvement or refinement.",
#     "part_of_speech": "noun",
#     "example_sentence": "Each iteration of the design process brought us closer to the final product."
#   }
# ]
# ```"""
#     if output.startswith("```json"):
#         output = output[len("```json"):].lstrip('\n') # 移除開頭標記和可能的換行符
#     if output.endswith("```"):
#         output = output[:-len("```")].rstrip('\n') # 移除結尾標記和可能的換行符
#     output_json = json.loads(output)
#     print(output_json)