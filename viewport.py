# coding: utf-8

import time
import json
import tkinter as tk

from APIRequest import APIRequest
import mapmaker
import misc
		
NESW = tk.NE + tk.SW

# Button for going back, added to every new page.
class BackButton(tk.Frame): 
    def __init__(self, window):
        tk.Frame.__init__(self, window.frame)
        self.button = tk.Button(self, text="Gå tillbaka", command=window.mainMenu)
        self.button.pack(fill=tk.BOTH, expand=True)

# Main window.
class Viewport(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.api = APIRequest()

        self.lastDepStop = ""
        self.lastTripDepStop = ""
        self.lastTripArrStop = ""

        self.frame = tk.Frame(self)
        self.frame.pack()
        self.mainMenu()

    # Clears the frame so new stuff can be put in.
    def clearFrame(self): 
        for widget in self.frame.winfo_children():
            widget.destroy()

    # Create the main menu.
    def mainMenu(self): 
        self.clearFrame()

        tk.Label(self.frame, text="Välkommen till planeraren!", font='bold', padx=10, pady=5).pack(fill=tk.BOTH, expand=True)
        tk.Button(self.frame, text="Reseplanerare", padx=5, pady=2, command=self.tripPlanMenu).pack(fill=tk.BOTH, expand=True)
        tk.Button(self.frame, text="Avgångar", padx=5, pady=2, command=self.departuresMenu).pack(fill=tk.BOTH, expand=True)
        tk.Button(self.frame, text="Ta mig hem", padx=5, pady=2, command=self.takeMeHomeMenu).pack(fill=tk.BOTH, expand=True)
        self.frame.mainloop()

    # Create menu for searching trips.
    def tripPlanMenu(self): 
        self.clearFrame()
        BackButton(self).grid(row=0, column=0, columnspan=4, sticky=NESW)

        tk.Label(self.frame, text="Reseplanerare", font="bold").grid(row=1, column=0, columnspan=4, sticky=NESW)

        tk.Label(self.frame, text="Fr\u00e5n").grid(row=2, column=0, columnspan=1, sticky=NESW)
        frombox = tk.Entry(self.frame)
        frombox.grid(row=2, column=1, columnspan=2, sticky=NESW)
        frombox.insert(tk.END, self.lastTripDepStop)
        tk.Button(self.frame, text="Rensa", command=lambda: frombox.delete(0, tk.END)).grid(row=2, column=3, columnspan=1, sticky=NESW)

        tk.Label(self.frame, text="Till").grid(row=3, column=0, columnspan=1, sticky=NESW)
        tobox = tk.Entry(self.frame)
        tobox.grid(row=3, column=1, columnspan=2, sticky=NESW)
        tobox.insert(tk.END, self.lastTripArrStop)
        tk.Button(self.frame, text="Rensa", command=lambda: tobox.delete(0, tk.END)).grid(row=3, column=3, columnspan=1, sticky=NESW)

        tk.Label(self.frame, text="Tid").grid(row=4, column=0, columnspan=1, sticky=NESW)
        timebox = tk.Entry(self.frame)
        timebox.grid(row=4, column=1, columnspan=2, sticky=NESW)
        timebox.insert(tk.END, time.strftime("%H:%M"))

        tk.Label(self.frame, text="Datum").grid(row=5, column=0, columnspan=1, sticky=NESW)
        datebox = tk.Entry(self.frame)
        datebox.grid(row=5, column=1, columnspan=2, sticky=NESW)
        datebox.insert(tk.END, time.strftime("%Y-%m-%d"))

        tk.Button(self.frame, text="Nu", command=lambda: self.setNow(timebox, datebox)).grid(row=4, column=3, rowspan=2, sticky=NESW)

        tk.Button(self.frame, text="Fler val", command=self.moreOptions).grid(row=6, column=0, columnspan=4, sticky=NESW)
        self.arr = tk.BooleanVar()
        self.smallChangeTime = tk.BooleanVar()
        self.notInUse = tk.BooleanVar()

        tk.Button(self.frame, text="Sök resa", command=lambda: misc.plan(self, frombox.get(), tobox.get(), timebox.get(), datebox.get(), 
                  self.arr.get(), self.smallChangeTime.get())).grid(column=0, columnspan=4, sticky=NESW)
        self.frame.bind("<Return>", lambda event: misc.plan(self, frombox.get(), tobox.get(), timebox.get(), datebox.get(),
                                                            self.arr.get(), self.smallChangeTime.get()))

        self.frame.mainloop()

    # Create box for more options when planning trip.
    def moreOptions(self): 
        root = tk.Toplevel()
        tk.Label(root, text="Fler val", font="bold").grid(row=0, column=0, columnspan=2, sticky=NESW)

        tk.Radiobutton(root, text="Ankomst", variable=self.arr, value=True).grid(row=1, column=0, columnspan=1, sticky=tk.N + tk.SW)
        tk.Radiobutton(root, text="Avg\u00e5ng", variable=self.arr, value=False).grid(row=1, column=1, columnspan=1, sticky=tk.N + tk.SW)

        tk.Checkbutton(root, text="Kort bytestid", variable=self.smallChangeTime).grid(row=2, column=0, columnspan=1, sticky=tk.N + tk.SW)

        tk.Checkbutton(root, text="Not in use", variable=self.notInUse).grid(row=2, column=1, columnspan=1, sticky=tk.N + tk.SW)

        tk.Button(root, text="Klar", command=root.destroy).grid(row=3, column=0, columnspan=2, sticky=NESW)

        root.mainloop()

    # Print the trip plan.
    def printPlan(self, trips, to, fr, frame=None):
        if frame is None:
            frame = self.frame
            self.clearFrame()
            BackButton(self).grid(column=0, columnspan=2, sticky=NESW)
        trip = []

        # If more than one alternative
        if type(trips) == list:
            for i in trips:
                trip.append(i.get("Leg"))
        # If only one alternative
        elif type(trips) == dict: 
            trip[0] = trips.get("Leg")

        tk.Label(frame, font='bold', text=f'Fr\u00e5n {fr} till {to}').grid(column=0, columnspan=2, sticky=NESW)
        

        for i in trip:
            self.printLeg(frame, i)

    # Prints each trip alternative.
    def printLeg(self, root, trip): 
        frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        frame.grid(column=0, columnspan=2, sticky=NESW)

        # If more than one leg (1+ changes)
        if type(trip) == list: 

            triptime, tH, tM = misc.tripTime(trip)

            labelText = f'Resa {trip[0].get("Origin").get("time")}-{trip[-1].get("Destination").get("time")} - Restid {str(tH)} h {str(tM)} min'

            tk.Label(frame, text= labelText, pady=5).grid(row=0, column=0, columnspan=2, sticky=NESW)
                                                                                          
            tk.Button(frame, text="Karta", command= lambda: mapmaker.geometryBackEnd(trip)).grid(row=1, column=0, columnspan=2, sticky=NESW)

            # Go through all legs and print them
            for i, leg in enumerate(trip):
                depTime = leg.get("Origin").get("time")
                arrTime = leg.get("Destination").get("time")
                if leg.get("Origin").get("rtTime"):
                    depDelay = misc.getDelay(leg.get("Origin")) 
                else:
                    depDelay = ""
                if leg.get("Destination").get("rtTime"):  
                    arrDelay = misc.getDelay(leg.get("Destination"))
                else:
                    arrDelay = ""

                if leg.get("type") == "WALK":
                    #Exclude walks inside the same stop.
                    if not leg.get("Origin").get("name") == leg.get("Destination").get("name"): 
                        tk.Label(frame,text=leg.get("name") + " till " + leg.get("Destination").get("name")).grid(row=i + 2, column=0, sticky=NESW)
                        tk.Label(frame, text=f'{depTime} - {arrTime}').grid(row=i + 2, column=1, sticky=NESW)


                else:
                    # Print line, destination and times
                    tk.Button(frame, text=leg.get("name") + " till " + leg.get("Destination").get("name"),
                           bg=leg.get("fgColor"), fg=leg.get("bgColor"),
                           command=lambda leg=leg: self.displayRoute(leg.get("JourneyDetailRef").get("ref")),
                           relief=tk.FLAT).grid(row=i + 2, column=0, sticky=NESW)
                    tk.Label(frame, text=f'{depTime}{depDelay} - {arrTime}{arrDelay}').grid(row=i + 2, column=1, sticky=NESW)

        # If only one leg. (No changes)
        elif type(trip) == dict: 
            triptime, tH, tM = misc.tripTime(trip)

            depTime = trip.get("Origin").get("time")
            arrTime = trip.get("Destination").get("time")
            if trip.get("Origin").get("rtTime"):
                depDelay = misc.getDelay(trip.get("Origin")) 
            else:
                depDelay = ""
            if trip.get("Destination").get("rtTime"):  
                arrDelay = misc.getDelay(trip.get("Destination"))
            else:
                arrDelay = ""

            tk.Label(frame, text=f'Resa {depTime}-{arrTime} - Restid {tH!s} h {tM!s} min', pady=5).pack(side=tk.TOP, fill=tk.X)
            tk.Button(frame, text="Karta", command= lambda: mapmaker.geometryBackEnd(trip.get("GeometryRef").get("ref"), trip.get("fgColor"))).pack(fill=tk.X)

            tk.Button(frame, text=trip.get("name") + " till " + trip.get("Destination").get("name"),
                   bg=trip.get("fgColor"), fg=trip.get("bgColor"),
                   command=lambda: self.displayRoute(trip.get("JourneyDetailRef").get("ref")),
                   relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X)
            tk.Label(frame, text=f'{depTime}{depDelay} - {arrTime}{arrDelay}').pack(side=tk.LEFT)


    def setNow(self, timebox, datebox): #Add current time and date to entry fields
        timebox.delete(0, tk.END)
        timebox.insert(tk.END, time.strftime("%H:%M"))
        datebox.delete(0, tk.END)
        datebox.insert(tk.END, time.strftime("%Y-%m-%d"))

    def displayRoute(self, url): # Display line, stops and times for one departure.
        route = self.api.getRoute(url)

        routeRoot = tk.Toplevel()

        # Get name of route ("Buss 50")
        try:
            name = route.get("JourneyName")[0].get("name")
        except KeyError:
            name = route.get("JourneyName").get("name")

        # Make names presentable
        name = name.replace("Bus", "Buss")
        name = name.replace("Sp\u00e5", "Sp\u00e5rvagn")
        name = name.replace("Reg T\u00c5G", "T\u00e5g")
        name = name.replace("V\u00e4s T\u00c5G", "V\u00e4stt\u00e5g")
        name = name.replace("Fär", "Färja")

        # Get destination ("Centralstationen")
        try:
            destination = route.get("Direction")[0].get("$")
            multipleDestionations = True
        except KeyError:
            destination = route.get("Direction").get("$")
            multipleDestionations = False

        # Store colour-dict in variable
        colour = route.get("Color")

        # Print out line and destination
        label = tk.Label(routeRoot, text= f'{name} mot {destination}', bg=colour.get("fgColor"), fg=colour.get("bgColor"))
        
        # Get labels if the line changes number/destination
        extras = []
        if multipleDestionations:
            direction = route.get("Direction")
            journeyName = route.get("JourneyName")
            stop = route.get("Stop")

            # Go through every change
            i = 1
            while i < len(direction):
                # Get the stop where it changes
                stopID = int(direction[i].get("routeIdxFrom"))
                fromStop = stop[stopID].get("name")

                # Get new line name and make them presentable
                name = journeyName[i].get("name")
                name = name.replace("Bus", "Buss")
                name = name.replace("Sp\u00e5", "Sp\u00e5rvagn")
                name = name.replace("Reg T\u00c5G", "T\u00e5g")
                name = name.replace("V\u00e4s T\u00c5G", "V\u00e4stt\u00e5g")
                name = name.replace("Fär", "Färja")

                # Create the label and add it to a list
                labelText = f'Blir {name} mot {direction[i].get("$")} vid {fromStop}'
                extras.append(tk.Label(routeRoot, text=labelText, bg=colour.get("fgColor"), fg=colour.get("bgColor")))
                i += 1



        # Determines how many columns are necessary
        if len(route.get("Stop")) > 60:
            columns = 6
        elif len(route.get("Stop")) > 30:
            columns = 4
        else:
            columns = 2

        # Grid the journey info    
        label.grid(sticky=NESW, row=0, column=0, columnspan=columns)
        
        if multipleDestionations:
            for i, value in enumerate(extras):
                value.grid(sticky=NESW, row=i+1, column = 0, columnspan=columns)

        # Print route and times
        for i, stops in enumerate(route.get("Stop")):
            column = 0
            row = i + len(extras)
            # Changes what column stuff is being put into.
            if len(route.get("Stop")) > 60:
                if i >= 2 * len(route.get("Stop")) // 3:
                    column = 4
                    row -= (2 * len(route.get("Stop")) // 3)
                elif i >= len(route.get("Stop")) // 3:
                    column = 2
                    row -= (len(route.get("Stop")) // 3)
                
            elif len(route.get("Stop")) > 30:
                if i >= len(route.get("Stop")) // 2:
                    column = 2
                    row -= (len(route.get("Stop")) // 2)
            
            # Prints name of stop 
            tk.Label(routeRoot, text=stops.get("name")).grid(sticky=NESW, row=row + 1, column=column)

            # Tries to get times. RT Dep -> TT Dep -> RT Arr -> TT Arr -> Error
            if not stops.get("rtDepTime"):
                if not stops.get("depTime"):
                    if not stops.get("rtArrTime"):
                        if not stops.get("arrTime"):
                            tk.Label(routeRoot, text="Error").grid(sticky=NESW, row=row + 1, column=column + 1)
                        else:
                            tk.Label(routeRoot, text="a(" + stops.get("arrTime") + ")").grid(sticky=NESW, row=row + 1, column=column + 1)
                    else:
                        delay = misc.getDelay(stops)
                        tk.Label(routeRoot, text=f'a{stops.get("arrTime")} {delay}').grid(sticky=NESW, row=row + 1, column=column + 1)
                else:
                    tk.Label(routeRoot, text="(" + stops.get("depTime") + ")").grid(sticky=NESW, row=row + 1, column=column + 1)
            else:
                delay = misc.getDelay(stops)
                tk.Label(routeRoot, text=f'{stops.get("depTime")} {delay}').grid(sticky=NESW, row=row + 1, column=column + 1)

        tk.Button(routeRoot, text="Karta", command= lambda: mapmaker.geometryBackEnd(route.get("GeometryRef").get("ref"), colour.get("fgColor"))).grid(column=0, columnspan=columns, sticky=NESW)

        tk.Button(routeRoot, text="Stäng", command=routeRoot.destroy).grid(column=0, columnspan=columns, sticky=NESW)

    # Create menu for choosing stop and times for viewing departures.
    def departuresMenu(self):
        self.clearFrame()
        BackButton(self).grid(row=0, column=0, columnspan=3, sticky=NESW)

        tk.Label(self.frame, text="Avgångar", font="bold").grid(row=1, column=0, columnspan=3, sticky=NESW)

        tk.Label(self.frame, text="Hållplats").grid(row=2, column=0, columnspan=1, sticky=NESW)
        stopbox = tk.Entry(self.frame)
        stopbox.grid(row=2, column=1, columnspan=1, sticky=NESW)
        stopbox.insert(tk.END, self.lastDepStop)
        tk.Button(self.frame, text="Rensa", command=lambda: stopbox.delete(0, tk.END)).grid(row=2, column=2, columnspan=1, sticky=NESW)

        tk.Label(self.frame, text="Tid").grid(row=3, column=0, columnspan=1, sticky=NESW)
        timebox = tk.Entry(self.frame)
        timebox.grid(row=3, column=1, columnspan=1, sticky=NESW)
        timebox.insert(tk.END, time.strftime("%H:%M"))

        tk.Label(self.frame, text="Datum").grid(row=4, column=0, columnspan=1, sticky=NESW)
        datebox = tk.Entry(self.frame)
        datebox.grid(row=4, column=1, columnspan=1, sticky=NESW)
        datebox.insert(tk.END, time.strftime("%Y-%m-%d"))

        tk.Button(self.frame, text="Nu", command=lambda: self.setNow(timebox, datebox)).grid(row=3, column=2, rowspan=2, sticky=NESW)

        tk.Button(self.frame, text="Sök", command=lambda: misc.dep(self, stopbox.get(), timebox.get(), datebox.get())).grid(
            row=5, column=0, columnspan=3, sticky=NESW)
        self.frame.bind("<Return>", lambda event: misc.dep(self, stopbox.get(), timebox.get(), datebox.get()))

        self.frame.mainloop()

    # Print the departures for the stop. Line, destination, time and delay.
    def printDepartures(self, departures, stopname, date, time_):
        self.clearFrame()
        BackButton(self).grid(row=0, column=0, columnspan=3, sticky=NESW)

        # Print stopname and time.
        headline = tk.Label(self.frame, text=f'Avgångar från {stopname} {time_} {date}', pady=5, padx=10)
        headline.grid(row=1, column=0, columnspan=3, sticky=tk.E + tk.W)

        # Go through all departures and add buttons to printJourney.
        for i, departure in enumerate(departures):
            tk.Label(self.frame, text=departure.get("sname"), bg=departure.get("fgColor"),
                  fg=departure.get("bgColor")).grid(row=i + 2, column=0, sticky=NESW)
            tk.Button(self.frame, text=departure.get("direction"),
                   command=lambda departure=departure: self.displayRoute(departure.get("JourneyDetailRef").get("ref"))).grid(
                row=i + 2, column=1, sticky=tk.E + tk.W)

            if not departure.get("rtTime"):
                tk.Label(self.frame, text="ca " + departure.get("time")).grid(row=i + 2, column=2, sticky=NESW)
            else:

                delay = misc.getDelay(departure)

                tk.Label(self.frame, text=f'{departure.get("time")} {delay}').grid(row=i + 2, column=2, sticky=NESW)

    # Not implemented
    def takeMeHomeMenu(self):
        pass

    

if __name__ == "__main__":        
	print("This file is only supposed to be used as a module.")
