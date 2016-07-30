import config
import telebot
import xmltodict
import json

bot = telebot.TeleBot(config.token)


# Works! (Sort of. File mimics API responce)
# Absorb and parse list of events, return them in appropriate format
# [ ["nameA","Date From Timestamp in Moscow Time", "Club", "Genre", "Ticket(?)", ]  ]
def getEventList():
	#temporal solution, because we contected ActionList maintainers to get API-key 
	#and they haven't answered
	listOfEvents = []
	w = open("ex_q.xml","r", encoding="UTF-8")
	o = xmltodict.parse(w.read())
	for i in list(o["events"].items())[0][1]:
		listOfEvents.append(dict(i))
	return listOfEvents
		
def createCityEventResponce():
	resp = "Events for today:\n\n"
	for i,e in enumerate(getEventList()):
		resp += str(i+1) + ") "
		resp += e["title"] + " - " + e["date"].split()[1] + "\n"
		resp += dict(e["club"])["club_name"] + "\n" + "/event_"+e["id"]
		resp += "\n\n"
	return resp

# Works! 
#Get city and show list of events)
@bot.message_handler(commands=['city_Moscow'])
def sendEventList(message): 
    #print(message.chat.id, message.text)
    bot.send_message(message.chat.id, createCityEventResponce())


#Get event and show: a) Details. b) Send sample tracks
@bot.message_handler(func=lambda m: m.text.startswith("/event"))
def eventDetails(message): 
    print(message.chat.id, message.text)
    #bot.send_message(message.chat.id, "")

if __name__ == '__main__':
	bot.polling(none_stop=True)
    