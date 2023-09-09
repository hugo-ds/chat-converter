import unittest
import chat_to_subtitle

class TestChatToAss(unittest.TestCase):

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
        
    def test_is_out_of_range_when_comment_time_is_negative_value_returns_true(self):
        comment = {
            'content_offset_seconds': -1
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
    #  is_banned_user
    #===================================================       
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
