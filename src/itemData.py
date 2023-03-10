from common import *
    
def variabled(num):
    binList = binarize(num)
    if (binList[6] == False) and (binList[7] == False):
        beg = "Task"
        return(beg + " " + chr(ord("A") + num))
    elif (binList[6] == True) and (binList[7] == False):
        beg = "Char"
        return(beg + " " + chr(ord("A") + num - 0x40))
    elif (binList[6] == False) and (binList[7] == True):
        beg = "System"
        return(beg + " " + chr(ord("A") + num - 0x80))
    elif (binList[6] == True) and (binList[7] == True):
        beg = "Data"
        names = [ "X Coord.", "Y Coord.", "Map X Coord.", "Map Y Coord.", "Parent X Coord.", "Parent Y Coord.", "Time", "Round Number" ]
        return(beg + " " + names[num - 0xC0])

def explicate(section, theType, scriptName):
    itemTypeDict = { 0: "Header", 12: "Image", 1: "Move Frame", 25: "Defense Frame", 24: "Attack Frame", 23: "Reaction Frame", 3: "Sound",
        30: "Cancel Condition", 35: "Color Modification", 4: "Object", 31: "Variable Fork", 2: "Detect Skill Fork", 22: "Detect Condition Fork",
        32: "Detect Random Fork", 36: "Detect Command Input Fork", 10: "Go To Skill", 11: "Call Skill", 9: "Loop Skill", 7: "Change Partner Place",
        20: "Change Partner Skill", 16: "Special Gauge Fork", 17: "Life Gauge Fork", 21: "Change Gauge", 14: "BG Scenery", 26: "Time Stop",
        37: "After Image", 5: "End Skill" }
    itemType = itemTypeDict[section[0]]
    params = [int.from_bytes(section[x:(x + 2)], "little") for x in range(1, 16, 2)]
    if (itemType == "Header"):
        if (theType == "player"):
            return({ "Type": itemType, "Skill Level": int.from_bytes(section[2:4], "little") })
        elif (theType == "stage"):
            binList = binarize(section[1])
            return({ "Type": itemType, "Horizontal Wrap": binList[1], "Vertical Wrap": binList[2], "Uses X Increase": binList[3],
                "Uses Y Increase": binList[4], "X Bounds Increase": abs(signed(int.from_bytes(section[2:4], "little"))),
                "Y Bounds Increase": abs(signed(int.from_bytes(section[4:6], "little"))) })
        elif (theType == "demo"):
            return({ "Type": itemType })
        elif (theType == "basic"):
            basicNames = open("basicScripts.txt", "rt")
            try:
                currentScript = basicNames.read().split("\n").index(scriptName)
            except ValueError as error:
                currentScript = -1
            basicNames.close()
            if (currentScript == 1):
                locs = ["Left", "Right"]
                return({ "Type": itemType, "Number Position": locs[section[1]], "Letter Width": section[2] }) # width does nothing lol.
            elif (currentScript >= 13) and (currentScript <= 33):
                return({ "Type": itemType, "Duration": int.from_bytes(section[1:3], "little") / 100 })
            elif (currentScript == 71):
                return({ "Type": itemType, "X Position": signed(int.from_bytes(section[1:3], "little")),
                    "Y Position": signed(int.from_bytes(section[3:5], "little")), "Number Offset": section[5] })
                # the offset seems to control how far away each number is from the point you chose, like on either side y'know?
            elif (currentScript in [72, 73, 74, 75, 79, 80, 82, 83, 88]):
                return({ "Type": itemType, "X Position": signed(int.from_bytes(section[1:3], "little")),
                    "Y Position": signed(int.from_bytes(section[3:5], "little")) })
            elif (currentScript == 76) or (currentScript == 77):
                return({ "Type": itemType, "X Position": signed(int.from_bytes(section[1:3], "little")),
                    "Y Position": signed(int.from_bytes(section[3:5], "little")), "X Width": miniSigned(section[5]),
                    "Y Width": miniSigned(section[6]) }) # the widths don't seem to really do anything here either. curiouser and curiouser.       
            else:
                return({ "Type": itemType })
    elif (itemType == "Image"):
        image = section[3]
        if (section[4] >= 0x40) and (section[4] < 0x60):
            x = True
            y = False
            image = image + ((section[4] - 0x40) * 256)
        elif (section[4] >= 0x80) and (section[4] < 0xA0):
            x = False
            y = True
            image = image + ((section[4] - 0x80) * 256)
        elif (section[4] >= 0xC0) and (section[4] < 0xE0):
            x = True
            y = True
            image = image + ((section[4] - 0xC0) * 256)
        else:
            x = False
            y = False
            if (section[4] == 1):
                image = image + 256

        return({ "Type": itemType, "Image ID": image, "Wait Time": params[0] / 100, "X Position": signed(params[2]), "Y Position": signed(params[3]),
            "X Flip Image": x, "Y Flip Image": y, "Immutable Direction": bool(params[4]) })
    elif (itemType == "Move Frame"):
        binList = binarize(params[4])
        return({ "Type": itemType, "X Move": signed(params[1]), "Y Move": signed(params[2]), "X Gravity": signed(params[0]),
            "Y Gravity": signed(params[3]), "Adds On": binList[0], "XM Ignore": binList[1], "YM Ignore": binList[2], "XG Ignore": binList[3],
            "YG Ignore": binList[4] })
    elif (itemType == "Defense Frame"):
        binList = binarize(section[10])
        return({ "Type": itemType, "X Center": signed(params[0]), "Y Center": signed(params[1]), "X Size": signed(params[2]),
            "Y Size": signed(params[3]), "DF Slot": section[9], "Collision": binList[0], "Takes Damage": binList[1], "Throwable": binList[2],
            "Damage Mult": params[5] })
    elif (itemType == "Attack Frame"):
        binList = binarize(section[10])
        return({ "Type": itemType, "X Center": signed(params[0]), "Y Center": signed(params[1]), "X Size": signed(params[2]),
            "Y Size": signed(params[3]), "AF Slot": section[9], "Cancellable": binList[0], "Continues Damage": binList[1],
            "Damages If Blocked": binList[2], "Only Hits Blockers": binList[3], "Ignores On-Grounds": binList[4], "Ignores In-Airs": binList[5],
            "Unblockable": binList[6], "Only Hits If Continuing": binList[7], "Power": section[12] })
    elif (itemType == "Reaction Frame"):
        return({ "Type": itemType, "Standing Hit": params[0], "Crouching Hit": params[1], "Aerial Hit": params[2], "Standing Guard": params[3],
            "Crouching Guard": params[4], "Aerial Guard": params[5] })
    elif (itemType == "Sound"):
        return({ "Type": itemType, "Sound ID": int.from_bytes(section[2:4], "little") })
    elif (itemType == "Cancel Condition"):
        timing = [ "Never", "By Hit", "Always" ]
        if (section[1] <= 2):
            return({ "Type": itemType, "Checks": "Level", "Available": timing[section[1]], "Level Minimum": section[2], "Level Maximum": section[5] })
        else:
            return({ "Checks": "Skill", "Available": timing[section[1] - 8], "Special Skill": params[1] })
    elif (itemType == "Color Modification"):
        choices = [ "Revert", "Add And Half Transparent", "Add Colors Weirdly", "Full Black", "Add And Choose Opacity" ]
        return({ "Type": itemType, "Mode": choices[section[1]], "Red": miniSigned(section[2]) * (1 / 32), "Green": miniSigned(section[3]) * (1 / 32),
        "Blue": miniSigned(section[4]) * (1 / 32), "Alpha Ratio": section[5] * (1 / 32) })
    elif (itemType == "Object"):
        binList = binarize(section[1])
        if (binList[0] == False) and (binList[1] == False):
            depth = "Behind"
        elif (binList[0] == True) and (binList[1] == False):
            depth = "In Front"
        elif (binList[0] == False) and (binList[1] == True):
            depth = "Chosen"

        return({ "Type": itemType, "X Offset": signed(int.from_bytes(section[8:10], "little")),
            "Y Offset": signed(int.from_bytes(section[10:12], "little")), "Object Skill": int.from_bytes(section[2:4], "little"),
            "Object Skill Start": section[4], "Obj Slot": section[12], "Ignores Jump Skill": binList[2], "Has Shadow": binList[3],
            "Only Moves With Parent": binList[5], "Uses Stage Coords": binList[6], "Depth": depth, "Z Value": section[13],
            "Jump Skill for Parent": params[2], "Jump Skill Duration": section[7] })
        # jump skill does not return to the original. this feature seems to basically not work, so I am going to implement it as it
        # seems like it should work: the projectile runs its script on its own, and the player simultaneously performs the jump skill,
        # then returns to default. the one thing I was able to actually figure out is that the "speed" value is actually how many items
        # of the skill are resolved before it ends
    elif (itemType == "Variable Fork"):
        binList = binarize(section[5])
        # number calculation options
        if (binList[0] == False) and (binList[1] == False):
            calc = "No Change"
        elif (binList[0] == True) and (binList[1] == False):
            calc = "Replace"
        elif (binList[0] == False) and (binList[1] == True):
            calc = "Add"
        # condition branch options
        if (binList[2] == False) and (binList[3] == False):
            branch = "No Branch"
        elif (binList[2] == True) and (binList[3] == False):
            branch = "If Same"
        elif (binList[2] == False) and (binList[3] == True):
            branch = "If Greater"
        elif (binList[2] == True) and (binList[3] == True):
            branch = "If Lesser"

        return({ "Type": itemType, "Target Variable": variabled(section[4]), "Applied Constant": params[3], "Application Type": calc,
            "Apply Variable Instead": binList[7], "Applied Variable": variabled(section[6]), "Comparison Constant": params[4],
            "Jump Condition": branch, "Jump Skill ID": params[0], "Jump Skill Start": section[3] })
    elif (itemType == "Detect Skill Fork"):
        # all these only work if they happen to the opponent as a result of the move. makes sense, but good to know.
        div = [ "Deactivated", "On Landing", "On Hit", "On Blocked Hit", "On Wall Collision", "On Non-Consecutive Hits", "On Throw" ]
        return({ "Type": itemType, "Jump Condition": div[section[1]], "Jump Skill ID": int.from_bytes(section[2:4], "little"),
            "Jump Skill Start": section[4] })
    elif (itemType == "Detect Condition Fork"):
        # all these check what the user is doing, of course
        div = [ "Deactivated", "If Holding Block", "If Standing", "If Holding Crouch", "If Holding Forwards", "If Holding Backwards",
            "If Holding Up", "If Holding Down" ]
        return({ "Type": itemType, "Jump Condition": div[section[7]], "Negate Condition": bool(section[1]),
            "Jump Skill ID": int.from_bytes(section[2:4], "little"), "Jump Skill Start": section[4] })
    elif (itemType == "Detect Random Fork"):
        return({ "Type": itemType, "RandInt Max": params[0], "Minimum For Jump": params[1], "Jump Skill ID": int.from_bytes(section[6:8], "little"),
            "Jump Skill Start": section[8] })
    elif (itemType == "Detect Command Input Fork"):
        inputs = []
        for i in range(5):
            binList = binarize(params[i + 2])
            buttons = [ "A", "B", "C", "D", "E", "F" ]
            reference = [ "A", "B", "C", "D", "E", "F" ]
            for j in range(4, 10):
                if (binList[j] == False):
                    buttons.remove(reference[j - 4])

            # remember to flip when facing left
            directions = [ "Any", "None", "E", "SE", "S", "SW", "W", "NW", "N", "NE", "Anything W", "Anything N", "Anything E", "Anything S" ]
            if (len(bin(params[i + 2])) >= 6):
                theDir = directions[int("0b" + bin(params[i + 2])[-4:], 2)]
            else:
                theDir = directions[params[i + 2]]

            if (binList[12] == False) and (binList[13] == False):
                relation = "Unused"
            elif (binList[12] == False) and (binList[13] == True):
                relation = "End"
            elif (binList[12] == True) and (binList[13] == True):
                relation = "Continue"
            
            inputs.append([ relation, theDir, buttons ])           
        return({ "Type": itemType, "Time Limit": section[4], "Jump Skill ID": params[0], "Jump Skill Start": section[3], "input1": inputs[0],
            "input2": inputs[1], "input3": inputs[2], "input4": inputs[3], "input5": inputs[4] })
    elif (itemType == "Go To Skill"):
        # goes to skill, then reverts to default
        return({ "Type": itemType, "Jump Skill ID": params[0], "Jump Skill Start": section[3] })
    elif (itemType == "Call Skill"):
        # goes to skill, then picks up where it left off in the old skill (like a function)
        return({ "Type": itemType, "Jump Skill ID": params[0], "Jump Skill Start": section[3] })
    elif (itemType == "Loop Skill"):
        # loops X times, then picks up where it left off in the old skill (like a function)
        return({ "Type": itemType, "Loop Count": section[1], "Jump Skill ID": int.from_bytes(section[2:4], "little"), "Jump Skill Start": section[4] })
    elif (itemType == "Change Partner Place"):
        binList = binarize(section[1])
        # coordinates refer to the top left of the opponent's image. presumably this is also true for objects.
        return({ "Type": itemType, "Partner X": signed(int.from_bytes(section[4:6], "little")),
            "Partner Y": signed(int.from_bytes(section[6:8], "little")), "Partner Common Image": int.from_bytes(section[2:4], "little"),
            "Partner In Back": binList[0], "X Flip Target": binList[2], "Y Flip Target": binList[3], "Same???": binList[4] })
    elif (itemType == "Change Partner Skill"):
        # reaction values are from the reaction table, NOT the overall skill ID
        binList = binarize(section[1])
        return({ "Type": itemType, "Partner X": signed(int.from_bytes(section[4:6], "little")),
            "Partner Y": signed(int.from_bytes(section[6:8], "little")), "Partner Reaction ID": int.from_bytes(section[2:4], "little"),
            "Partner In Back": binList[0], "X Flip Target": binList[2] })
    elif (itemType == "Special Gauge Fork"):
        return({ "Type": itemType, "Bars Count": section[6], "Check If User Has Less Instead": bool(section[5]),
            "Success Change Amount": signed(params[3]), "Fail Jump Skill": int.from_bytes(section[2:4], "little"), "Fail Jump Skill Start": section[4] })
    elif (itemType == "Life Gauge Fork"):
        return({ "Type": itemType, "Life Count": section[6], "Check If User Has Less Instead": bool(section[5]),
            "Fail Jump Skill": int.from_bytes(section[2:4], "little"), "Fail Jump Skill Start": section[4] })
    elif (itemType == "Change Gauge"):
        return({ "Type": itemType, "User Life Change": signed(int.from_bytes(section[2:4], "little")),
        "User Special Change": signed(int.from_bytes(section[4:6], "little")), "Target Life Change": signed(int.from_bytes(section[6:8], "little")),
        "Target Special Change": signed(int.from_bytes(section[8:10], "little")) })
    elif (itemType == "BG Scenery"):
        binList = binarize(section[8])
        pals = [ "None", "Fade", "Blink", "Random" ]
        shakes = [ "None", "Decreasing", "Increasing", "Fixed", "Random" ]
        return({ "Type": itemType, "Palette Fade Type": pals[section[1]], "Palette Fade Duration": int.from_bytes(section[6:8], "little") / 100,
            "Affects User": binList[0], "Affects Opponent": binList[1], "Affects Stage": binList[2], "Affects System Event": binList[3],
            "Red": miniSigned(section[2]) * (1 / 32), "Blue": miniSigned(section[3]) * (1 / 32),
            "Green": miniSigned(section[4]) * (1 / 32), "Alpha Ratio": miniSigned(section[5])* (1 / 32),
            "X Shake Type": shakes[section[9]], "X Shake Duration": section[11] / 100, "X Shake Intensity": section[10],
            "Y Shake Type": shakes[section[12]], "Y Shake Duration": section[14] / 100, "Y Shake Intensity": section[13] })
       # for smooth fading, duration is how long it takes to get to full; it stays on until you turn it off. for blinking, it stops blinking after
       # the duration. also, what it fades to is determined by the color values--basically it adds and adds until it gets to what you put in.
       # for shaking, you either increase from 0 to the intensity, or decrease from the intensity to 0. it ends all on its own, thank god.
       # I think intensity is based on distance, not time. Testing shows that it shifts the image, then immediately shifts it back, every 10th
       # of a second. It seems to alternate up/down and left/right (in that order). based on essentially one test, intensity seems to be the
       # number of pixels shifted.
    elif (itemType == "Time Stop"):
        return({ "Type": itemType, "User Stop Duration": section[1] / 100, "Target Stop Duration": section[2] / 100 })
    elif (itemType == "After Image"):
        # this setting is very weird in that it keeps going after the move is over. it will continue making "after images" (sprites showing your
        # last X frames) until another AI deactivates it. during that time, images last for the Duration, and only X can exist at a time, with
        # possible new ones simply not showing up if there are too many out.
        choices = [ "Revert", "Add And Half Transparent", "Add Colors Weirdly", "Full Black", "Add And Choose Opacity" ]
        choices2 = [ "Deactivated", "None", "Fade", "Blink", "Random" ]
        return({ "Type": itemType, "Image Count": section[3], "Image Duration": section[4] / 100, "Color Mode": choices[section[5]],
            "Fading Mode": choices2[section[6]], "Red": miniSigned(section[7]) * (1 / 32), "Blue": miniSigned(section[8]) * (1 / 32),
            "Green": miniSigned(section[9]) * (1 / 32), "Alpha Ratio": miniSigned(section[10])* (1 / 32) })
    elif (itemType == "End Skill"):
        return({ "Type": itemType })