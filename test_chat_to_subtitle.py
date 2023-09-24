import unittest
import chat_to_subtitle
import click
from unittest.mock import patch

class TestChatToSubtitle(unittest.TestCase):

#===================================================
#  validate_time
#===================================================
    
    def test_validate_time_when_value_passed_is_well_formed_returns_false(self):
        ctx = None
        param = None
        value = '0:0:0'
        
        result = chat_to_subtitle.validate_time(ctx, param, value)
        self.assertEqual(['0', '0', '0'], result)
        
    def test_validate_time_when_value_passed_has_wrong_format_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = 'a:0:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
        
    def test_validate_time_when_value_passed_has_few_elements_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)

    def test_validate_time_when_value_passed_has_too_many_elements_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:0:0:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
    def test_validate_time_when_value_passed_has_negative_hour_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '-1:0:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
    def test_validate_time_when_value_passed_has_negative_minutes_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:-1:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
    def test_validate_time_when_value_passed_has_negative_seconds_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:0:-1'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
    def test_validate_time_when_value_passed_has_minutes_greater_than_60_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:61:0'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
    def test_validate_time_when_value_passed_has_seconds_greater_than_60_raise_BadParameter_error(self):
        ctx = None
        param = None
        value = '0:0:61'
        
        with self.assertRaises(click.exceptions.BadParameter):
            chat_to_subtitle.validate_time(ctx, param, value)
            
            
    #===================================================
    #  load_ban_file
    #===================================================
    def test_load_ban_file_when_banfile_is_none_returns_empty_lists(self):
        ban_file = None
        result = chat_to_subtitle.load_ban_file(ban_file)
        
        self.assertEqual(([], [], [], []), result)
        
    def test_load_ban_file_when_standard_ban_file_returns_standard_lists(self):
        ban_file = "ban.json"
        mock_dict = {
           "word_only": ["abc", "[a]+", "BibleThump","NotLikeThis"],
           
           "whole_comment": ["aaa", "bbb"],
           
           "user": ["1", "2", "3"],
           
           "critical_word": ["boring"]
        }
        
        with patch('chat_to_subtitle.load_json_file', return_value=mock_dict):
            result = chat_to_subtitle.load_ban_file(ban_file)
            
            self.assertEqual((["abc", "[a]+", "BibleThump","NotLikeThis"], ["aaa", "bbb"], ["1", "2", "3"], ["boring"]), result)

    def test_load_ban_file_when_loaded_dictionary_misses_a_key_raise_SystemExit(self):
        ban_file = "ban.json"
        # No "critical_word" key in mock_dick.
        mock_dict = {
           "word_only": ["abc", "[a]+", "BibleThump","NotLikeThis"],
           
           "whole_comment": ["aaa", "bbb"],
           
           "user": ["1", "2", "3"]
        }
        
        with patch('chat_to_subtitle.load_json_file', return_value=mock_dict):
            with self.assertRaises(SystemExit):
                chat_to_subtitle.load_ban_file(ban_file)
                
    def test_load_ban_file_when_loaded_dictionary_contains_non_list_value_raise_SystemExit(self):
        ban_file = "ban.json"
        # No "critical_word" key in mock_dick.
        mock_dict = {
           "word_only": ["abc", "[a]+", "BibleThump","NotLikeThis"],
           
           "whole_comment": ["aaa", "bbb"],
           
           "user": ["1", "2", "3"],
           
           "critical_word": "word"
        }
        
        with patch('chat_to_subtitle.load_json_file', return_value=mock_dict):
            with self.assertRaises(SystemExit):
                chat_to_subtitle.load_ban_file(ban_file)
    


    #===================================================
    #  is_out_of_range
    #===================================================
    def test_is_out_of_range_when_comment_time_is_inside_of_range_returns_false(self):
        comment = {
            'content_offset_seconds': 50
        }
        result = chat_to_subtitle.is_out_of_range(comment, 20, 100)
        self.assertEqual(False, result)
        
    def test_is_out_of_range_when_comment_time_is_before_start_time_returns_true(self):
        comment = {
            'content_offset_seconds': 10
        }
        result = chat_to_subtitle.is_out_of_range(comment, 20, 100)
        self.assertEqual(True, result)

    def test_is_out_of_range_when_comment_time_is_after_end_time_returns_true(self):
        comment = {
            'content_offset_seconds': 101
        }
        result = chat_to_subtitle.is_out_of_range(comment, 20, 100)
        self.assertEqual(True, result)
        
    def test_is_out_of_range_when_comment_time_is_equal_to_start_time_returns_false(self):
        comment = {
            'content_offset_seconds': 20
        }
        result = chat_to_subtitle.is_out_of_range(comment, 20, 100)
        self.assertEqual(False, result)
        
    def test_is_out_of_range_when_comment_time_is_equal_to_end_time_returns_false(self):
        comment = {
            'content_offset_seconds': 100
        }
        result = chat_to_subtitle.is_out_of_range(comment, 20, 100)
        self.assertEqual(False, result)       

    #===================================================
    #  is_banned_comment
    #===================================================
    def test_is_banned_comment_when_banned_words_is_empty_returns_false(self):
        comment = {
            'message': {
                'body': ""
            }
        }
        result = chat_to_subtitle.is_banned_comment(comment, [])
        self.assertEqual(False, result)
                   
    
    def test_is_banned_comment_when_exist_a_banned_word_in_the_comment_returns_true(self):
        comment = {
            'message': {
                'body': "aaa"
            }
        }
        result = chat_to_subtitle.is_banned_comment(comment, ['a'])
        self.assertEqual(True, result)
        
    def test_is_banned_comment_when_does_not_exist_a_banned_word_in_the_comment_returns_false(self):
        comment = {
            'message': {
                'body': "aaa"
            }
        }
        result = chat_to_subtitle.is_banned_comment(comment, ['BBB'])
        self.assertEqual(False, result)
        
    #===================================================
    #  is_banned_user    #===================================================       
    def test_is_banned_user_when_banned_users_is_empty_returns_false(self):
        comment = {
            'commenter': {
                'name':'',
                '_id':''
            }}
        result = chat_to_subtitle.is_banned_user(comment, [])
        self.assertEqual(False, result)
        
    def test_is_banned_user_when_username_is_banned_returns_true(self):
        comment = {
            'commenter': {
                'name':'name-A',
                '_id':'id-A'
            }}
        result = chat_to_subtitle.is_banned_user(comment, ['name-A'])
        self.assertEqual(True, result)
        
    def test_is_banned_user_when_userid_is_banned_returns_true(self):
        comment = {
            'commenter': {
                'name':'name-A',
                '_id':'id-A'
            }}
        result = chat_to_subtitle.is_banned_user(comment, ['id-A'])
        self.assertEqual(True, result)
        
    #===================================================
    #  clean_up_comment    #=================================================== 
        
    #===================================================
    #  substitute_text    #=================================================== 
    def test_substitute_text_when_word_with_periods_are_passed_returns_word_with_spaces(self):
        comment = {
            'message': {
                'body': ".a.b.c.d."
            }
        }
        result = chat_to_subtitle.substitute_text(comment)
        self.assertEqual(" a b c d ", result)
        
    def test_substitute_text_when_lots_of_ws_returns_www(self):
        comment = {
            'message': {
                'body': "wwwwWWWWｗｗｗｗＷＷＷＷ"
            }
        }
        result = chat_to_subtitle.substitute_text(comment)
        self.assertEqual("www", result)

    #===================================================
    #  convert_hms_to_seconds
    #=================================================== 
    
    def test_convert_hms_to_seconds_when_time_is_zero_returns_zero(self):
        hms = ['0', '0', '0']
        result = chat_to_subtitle.convert_hms_to_seconds(hms)
        self.assertEqual(0, result)
        
    def test_convert_hms_to_seconds_when_time_is_6h32min17s_returns_23537(self):
        hms = ['6', '32', '17']
        result = chat_to_subtitle.convert_hms_to_seconds(hms)
        self.assertEqual(23537, result)
        
        