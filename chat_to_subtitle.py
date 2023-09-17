#========================================================
#  Convert twitch comments downloaded by TwitchDownloader to ass subtitle format.
#========================================================

# Todo:
# - Exception handling (File not found,...)
# - Add styles to comments (color, big, static)
# - Add tests
# - Divide chat: per 3 hour, or eg. 3分割 指定時間でコメント分割
# - Smaller functions
# - Implement better comments display algorythm
# - Ban a user that posted specific comment
# - Make a class of arguments?


import json, os, sys, re, click
from datetime import timedelta
from rich import print

# Validate start time and end time parameters.
# If end time was not specified, do not check time range. 
# Include all comments from start time to video end.
def validate_time(ctx, param, value):   
    try:
        splitted = value.split(':')
        
        if len(splitted) != 3:
            raise click.BadParameter("format must be 'h:m:s'")
            
        # Negative values not allowed.
        if (int(splitted[0]) < 0 or 
            int(splitted[1]) < 0 or 
            int(splitted[2]) < 0):
            raise click.BadParameter("Values must be positive numbers.")
        
        # Minutes or seconds greater than 60 not allowed.
        if (int(splitted[1]) > 60 or 
            int(splitted[2]) > 60):
            raise click.BadParameter("Minutes and seconds must be 60 or lower.")
        
        return splitted
        
    except ValueError:
        raise click.BadParameter("The format must be 'h:m:s'")


@click.command()
@click.option('--input-file', '-i', default='chat.json', show_default=True, required=True, help='The input file: chat file in json format.')
@click.option('--output-file', '-o', default='chat.ass', show_default=True, help='The output file: chat subtitle in ass format.')
@click.option('--ban-file', '-b', help='The ban comments and users file.')
@click.option('--start-time', '-s', type=click.UNPROCESSED, callback=validate_time, default='0:0:0', help='Start time of comments to output. Parameter format: h:m:s')
@click.option('--end-time', '-e',  type=click.UNPROCESSED, callback=validate_time, default='0:0:0', help='End time of comments to output. Parameter format: h:m:s')
@click.option('--play-res-x', '-x', type=click.IntRange(1), default=854, help='Comment player\'s x resolution.')
@click.option('--play-res-y', '-y', type=click.IntRange(1), default=480, help='Comment player\'s y resolution.')
@click.option('--font-size', '-f', type=click.IntRange(1), default=36, help='Font size of comments.')
@click.option('--visible-time', '-v', type=click.IntRange(1), default=7, help='Time in seconds that comments stay visibles.')
def convert_chat(input_file, output_file, ban_file, start_time, end_time, play_res_x, play_res_y, font_size, visible_time):

    # Load the input file (json with comments).
    data = load_json_file(input_file)

    comments = data['comments'] # Load all comments.

    start_time_in_seconds = convert_hms_to_seconds(start_time)
    end_time_in_seconds = convert_hms_to_seconds(end_time)
    
    # Validate start time and end time combination.
    if (end_time_in_seconds != 0 and 
        start_time_in_seconds == end_time_in_seconds):
        sys.exit(f'Start time {start_time_in_seconds}s and end time {end_time_in_seconds}s are the same. Change one of them.')
    
    elif (end_time_in_seconds != 0 and 
    start_time_in_seconds > end_time_in_seconds):
        sys.exit(f'Start time {start_time_in_seconds}s is greater than end time {end_time_in_seconds}s. Change one of them.')

    print(f'Comments before: {len(comments)}')
    print(f'start_time: {start_time}')
    print(f'end_time {end_time}')
    
    # Process each comment and return formatted list.
    items = process_comments(comments, start_time_in_seconds, end_time_in_seconds, ban_file, play_res_y, font_size)

    # Write comments in the items list to subtitle file.
    output_as_subtitle(items, play_res_x, play_res_y,  font_size, output_file, visible_time)


# Load a json file (with comments data).
def load_json_file(input_file):
    try: 
        with open(input_file, mode='r', encoding="utf8") as f:
            return json.load(f)
            
    except ValueError:
        sys.exit(f'The {input_file} is not a json file.')
        
    except FileNotFoundError as e:
        sys.exit(f'File {input_file} not found. Confirm the file name.')


# Read a file and return a list of lines.
def load_file(input_file):       
    try:
        with open(input_file, mode='r', encoding="utf8") as f:
            lines = f.readlines()
        return [s.strip() for s in lines]
    except FileNotFoundError as e:
        sys.exit(f'File {input_file} not found. Confirm the file name')


# Load the ban file with a list of dictionaries.
#[
#	{
#		'ban_mode': 'word, comment or user',
#		'target': 'word(regex), user id or user name',
#		'is_user_banned': true or false # Not implemented
#	},
#]
#
def load_ban_file(ban_file):
    if ban_file == None:
        return [], [], []

    dicts = load_json_file(ban_file)['data']
    remove_words = [] # List of words. (Delete the word only)
    banned_words = [] # List of words. (Delete whole comment)
    banned_users = [] # List of user ids and names.
    
    for dict in dicts:
        ban_mode = dict['ban_mode']
        target = dict['target']
        
        if ban_mode == 'word':
            remove_words.append(target)
            
        elif ban_mode == 'comment':
            banned_words.append(target)
            
        elif ban_mode == 'user':
            banned_users.append(target)
    
    return remove_words, banned_words, banned_users


# Check if the comment time is out of range (between start and end time).
def is_out_of_range(comment, start_time, end_time):  
    time = comment['content_offset_seconds']
    
    if time < start_time:
        return True
        
    if end_time != 0 and time > end_time:
        return True
    
    return False


# Check if the comment includes a banned word.
def is_banned_comment(comment, banned_words):       
    if len(banned_words) == 0:
        return False

    for banned_word in banned_words:
        if banned_word in comment['message']['body']:
            return True

    return False


# Check if the comment is from a banned user.
def is_banned_user(comment, banned_users):    
    if len(banned_users) == 0:
        return False
        
    if (comment['commenter']['name'] in banned_users or comment['commenter']['_id'] in banned_users):
        return True
        
    return False


# Remove words from a comment.
def clean_up_comment(comment, remove_words):
    message = comment['message']['body']
    
    if len(remove_words) == 0:
        return message
        
    for remove_word in remove_words:
        message = re.sub(remove_word, '', message)
        
    return message.strip()


# Convert a list: [hour, minutes, seconds] to seconds.
def convert_hms_to_seconds(hms):
    td = timedelta(hours=int(hms[0]), minutes=int(hms[1]), seconds=int(hms[2]))
    return int(td.total_seconds())


# TODO: Create smaller funcitions.
def process_comments(comments, start_time_in_seconds, end_time_in_seconds, ban_file, play_res_y, font_size):
    deleted_comment_counter = 0
    items = [] # Store processed comment data.
    
    # List of user names, ids and comments that are banned.
    # If ban file was not passed as command line argument, return empty lists.
    remove_words, banned_words, banned_users = load_ban_file(ban_file)
    
    for comment in comments:
        #
        # TODO: validate comment here. Fields exist, etc.
        #
    
    
        if is_out_of_range(comment, start_time_in_seconds, end_time_in_seconds):
            # skip out of range comment.
            continue

        if (is_banned_comment(comment, banned_users) or is_banned_user(comment, banned_words)):
            # Delete a comment of a banned user or containing a banned word.
            deleted_comment_counter = deleted_comment_counter + 1
            continue
        
        # Substitute . to white space (. causes file loading error)
        message = comment['message']['body'].replace('.', ' ')
        
        # Delete undesired words from a comment.
        message = clean_up_comment(comment, remove_words)
        
        if len(message) == 0:
            # Skip empty comment.
            deleted_comment_counter = deleted_comment_counter + 1
            continue
        
        i = len(items) # Processed comments quantity.
        
        # Load comment time and adjust it considering the start time.
        time = comment['content_offset_seconds'] - start_time_in_seconds
        
        # TODO: Implement better comments display algorythm
        # Define where to display a comment.
        # If the current comment is the 1st comment, show it in the first line.
        # or If the comment's time is greater than 1s after the previous comment, show it in the first line.
        # or If the previous comment was displayed in the last line of display range, show it in the first line.
        # Otherwise, show the comment in the next line.
        if (i == 0 or
            time - items[i-1]['time'] > 1 or
            items[i-1]['y'] >= (play_res_y - font_size * 2)):
            y = 0
        else:
            y = items[i-1]['y'] + font_size
        
        item = {'time': time, 'message': message, 'y': y}
        items.append(item)

    print(f'Comments after:  {len(items)}')
    print(f'Comments deleted: {deleted_comment_counter}')
    
    return items
    

# Convert items dictionary and write as subtitle file.
def output_as_subtitle(items, play_res_x, play_res_y,  font_size, output_file, visible_time):
    # Color: &H33BBGGRR
    s = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
Aspect Ratio: {play_res_x}:{play_res_y}
Collisions: Normal
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Danmaku2ASS, sans-serif, {font_size}, &H33FFFFFF, &H33FFFFFF, &H33000000, &H33000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 7, 0, 0, 0, 0
Style: danmakuBlue, sans-serif, {font_size}, &H33FF0000, &H33FFFFFF, &H33000000, &H33000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 7, 0, 0, 0, 0
Style: danmakuRed, sans-serif, {font_size}, &H330000FF, &H33FFFFFF, &H33000000, &H33000000, 0, 0, 0, 0, 100, 100, 0.00, 0.00, 1, 1, 0, 7, 0, 0, 0, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # f string doesn't accept backslash.
    newline = '\n'
    move_command = '\move'

    # Write the comments as subtitle.
    with open(output_file, mode='w', encoding="utf8") as f:
        f.write(s) # Write file header.
        
        for item in items:
            time = item['time']
            td1 = str(timedelta(seconds=time)) + '.00'
            td2 = str(timedelta(seconds = time + visible_time)) + '.00'
            
            message = item['message']
            
            y = item['y'] # Comment's height
            
            x2 = font_size * len(message) * -1 # Comment's length (display speed)

            # Write a comment to output file.
            f.write(f'Dialogue: 2,{td1},{td2},Danmaku2ASS,,0000,0000,0000,,{{{move_command}(854,{str(y)},{str(x2)},{str(y)})}}{message}{newline}')


if __name__ == '__main__':
    convert_chat()
