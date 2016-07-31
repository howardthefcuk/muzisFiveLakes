import config
import telebot
import xmltodict
import json
import requests
from urllib.request import urlopen
from telebot import types


bot = telebot.TeleBot(config.token)


# Absorb and parse list of events, return them in appropriate format
# [ ["nameA","Date From Timestamp in Moscow Time", "Club", "Genre", "Ticket(?)", ]  ]
def getEventList(city):
	#temporal solution, because we contected ActionList maintainers to get API-key 
	#and they haven't answered
	listOfEvents = []
	w = open(city+".xml","r", encoding="UTF-8")
	o = xmltodict.parse(w.read())
	for i in list(o["events"].items())[0][1]:
		listOfEvents.append(dict(i))
	return listOfEvents
		
# From the list of events creates a responce message
def createCityEventResponce(city):
	resp = "Events for today in " + city +":\n\n"
	for i,e in enumerate(getEventList(city)):
		resp += str(i+1) + ") "
		resp += e["title"] + " - " + e["date"].split()[1] + "\n"
		resp += dict(e["club"])["club_name"] + "\n" + "/event_"+e["id"]
		resp += "\n\n"
	return resp

# Use Muzis API to get list of names of files to download
# ['hdsud0srh6np.mp3', '0zfrdmic7h65.mp3', '4dxdbiud1tau.mp3', '33slgngns46w.mp3', '4vasuz9btb7c.mp3']
def getTrackIDs(performer):
	r = requests.post('http://muzis.ru/api/search.api', data = {'q_performer':performer})
	artId = json.loads(r.text)["performers"][0]["id"]
	r = requests.post('http://muzis.ru/api/get_songs_by_performer.api', data = {'performer_id':artId,'type':'3'})
	listOfSongs = json.loads(r.text)['songs']
	#a = [x["file_mp3"] for x in listOfSongs]
	return(listOfSongs[:5])	


#Welcome message - replace with 2 buttons
@bot.message_handler(commands=['start'])
def sendStartMessage(message): 	
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("/city_MSK")
    markup.add("/city_SPB")
    bot.send_message(message.chat.id, "This is Five Lakes Event BOt Demo.\nChoose your city:", reply_markup=markup)


#Get city from user and show list of events
@bot.message_handler(func=lambda m: m.text.startswith("/city_"))
def sendEventList(message): 
    #print(message.chat.id, message.text)
    city = message.text.split("_")[1]
    bot.send_message(message.chat.id, createCityEventResponce(city))


#Get event and show: a) Details. b) Send sample tracks
@bot.message_handler(func=lambda m: m.text.startswith("/event_"))
def eventDetails(message):
	evId = message.text.split("_")[1]
	for i in getEventList("MSK"):
		if i["id"] == evId:
			clubData = dict(i['club'])
			bot.send_message(message.chat.id, i["title"]+"\n"+i["date"]+"\n"+clubData["club_name"]+"\n"+clubData["club_adress"]+"\nTickets: "+i["ticket"])
			for i in getTrackIDs(i["title"]):
				url = 'http://f.muzis.ru/' + str(i["file_mp3"])
				result = urlopen(url).read()
				bot.send_audio(message.chat.id, result, 300, i["track_name"], i["performer"])

#test - Button
@bot.message_handler(commands=["test"])
def any_msg(message):
    


if __name__ == '__main__':
	#print(getEventList("MSK"))
	bot.polling(none_stop=True)
	
	