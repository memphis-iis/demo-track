import unittest

from demotrack.model import Subject

class SubjectTest(unittest.TestCase):
    def setUp(self):
        self.subj = Subject(
            subject_id="s1",
            first_name="Test",
            last_name="Dude",
            email="test@gmail.com",
            exp_condition="a"
        )

        self.item = {
            "subject_id": "s1",
            "first_name": "Test",
            "last_name": "Dude",
            "email": "test@gmail.com",
            "exp_condition": "a"
        }

    def tearDown(self):
        pass

    def assertNoErrors(self):
        e = list(self.subj.errors())
        self.assertTrue(len(e) < 1)

    def assertErrors(self):
        e = list(self.subj.errors())
        self.assertTrue(len(e) > 0)

    def testPersist(self):
        self.assertNoErrors()
        self.assertEqual(self.subj.get_item(), self.item)

        self.subj = Subject()
        self.subj.set_from_item(self.item)
        self.assertNoErrors()
        self.assertEqual(self.subj.get_item(), self.item)

    def testInvalidSID(self):
        self.assertNoErrors()
        self.subj.subject_id = None
        self.assertErrors()

    def testInvalidExpCond(self):
        self.assertNoErrors()
        self.subj.exp_condition = None
        self.assertErrors()
