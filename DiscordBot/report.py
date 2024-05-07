from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    ASKING_DETAILS = auto()
    BLACKMAIL_CHECK_PREVIOUS = auto()
    BLACKMAIL_THREAT_SAFETY = auto()
    BLACKMAIL_CONTACT_AUTHORITIES = auto()
    REVIEW_REPORT = auto()
    REPORT_COMPLETE = auto()

class Reason(Enum):
    UNIDENTIFIED = "unidentified"
    SUSPICIOUS_LINK = "suspicious link"
    BLACKMAIL = "blackmail"
    HARASSMENT = "harassment"
    SPAM = "spam"
    OTHER = "other"

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    
    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.report_details = {}
        self.reason = Reason.UNIDENTIFIED 
    
    async def handle_message(self, message):
        if message.content.lower() == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled. Thank you for your vigilance!"]
        
        if message.content.lower() == self.HELP_KEYWORD:
            return ["Help: Copy the link of the message you want to report and paste it here. Say `cancel` to exit the reporting process."]
        
        if self.state == State.REPORT_START:
            self.state = State.AWAITING_MESSAGE
            return ["Thank you for starting the reporting process. Please copy and paste the link to the message you want to report."]
        
        if self.state == State.AWAITING_MESSAGE:
            link_pattern = re.compile('/(\d+)/(\d+)/(\d+)')
            match = link_pattern.search(message.content)
            if match:
                guild_id, channel_id, message_id = match.groups()
                guild = self.client.get_guild(int(guild_id))
                channel = guild.get_channel(int(channel_id))
                try:
                    self.message = await channel.fetch_message(int(message_id))
                    self.state = State.MESSAGE_IDENTIFIED
                    return ["Message found:", f"```{self.message.author.name}: {self.message.content}```", \
                            "What is your reason for reporting this message: suspicious link, blackmail, harassment, spam, other?"]
                except discord.NotFound:
                    return ["Message not found. Please check the link and try again."]
            else:
                return ["Invalid link. Please check and paste the link again."]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            reason_input = message.content.strip().lower()
            if reason_input in [e.value for e in Reason]:
                self.reason = Reason[reason_input.replace(" ", "_").upper()]
                if self.reason == Reason.BLACKMAIL:
                    self.state = State.BLACKMAIL_CHECK_PREVIOUS
                    return ["Have you been blackmailed by this person before? (yes/no)"]
            else:
                self.reason = Reason.OTHER
            print(self.reason)
            self.state = State.ASKING_DETAILS
            return [f"What details can you provide about the {reason_input}? (e.g., how many messages have you received, any money lost, any personal information shared, etc)"]
        
        if self.state == State.BLACKMAIL_CHECK_PREVIOUS:
            self.report_details['previous_blackmail'] = message.content.lower() in ['yes', 'y']
            self.state = State.BLACKMAIL_THREAT_SAFETY
            return ["Do you feel an immediate threat to your safety? (yes/no)"]
        
        if self.state == State.BLACKMAIL_THREAT_SAFETY:
            self.report_details['threat_to_safety'] = message.content.lower() in ['yes', 'y']
            self.state = State.BLACKMAIL_CONTACT_AUTHORITIES
            return ["Have you contacted the authorities? (yes/no)"]
        
        if self.state == State.BLACKMAIL_CONTACT_AUTHORITIES:
            self.report_details['contacted_authorities'] = message.content.lower() in ['yes', 'y']
            self.state = State.REVIEW_REPORT
            return ["Review your report:", f"Reason: {self.reason.value}", 
                    f"Previous Blackmail: {self.report_details['previous_blackmail']}",
                    f"Threat to Safety: {self.report_details['threat_to_safety']}",
                    f"Contacted Authorities: {self.report_details['contacted_authorities']}",
                    "Does everything look correct? (yes/no)"]
        
        if self.state == State.ASKING_DETAILS:
            self.report_details['details'] = message.content
            self.state = State.REVIEW_REPORT
            return ["Review your report:", f"Reason: {self.reason.value}", f"Details: {self.report_details['details']}", \
                    "Does everything look correct? (yes/no)"]
        
        if self.state == State.REVIEW_REPORT:
            if message.content.lower() in ['yes', 'y']:
                self.state = State.REPORT_COMPLETE
                return ["Report submitted. We will review and take appropriate actions. Thank you."]
            else:
                self.state = State.REPORT_START
                return ["Let's start over. Please copy and paste the link to the message you want to report."]
        
        return []
    
    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
