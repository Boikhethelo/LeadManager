import unittest
from src import LeadData 

class TestLeadData(unittest.TestCase):

    def setUp(self):
        self.ld = LeadData()
        self.ld.data = {
            "companies": [
                {"CompanyID": "1", "Name": "TechCorp", "Industry": "Software"},
                {"CompanyID": "2", "Name": "HealthPlus", "Industry": "Healthcare"}
            ],
            "contacts": [
                {"ContactID": "101", "Name": "John Doe", "CompanyID": "1"},
                {"ContactID": "102", "Name": "Jane Smith", "CompanyID": "2"}
            ],
            "leads": [
                {"LeadID": "201", "CompanyID": "1", "Status": "Hot"},
                {"LeadID": "202", "CompanyID": "2", "Status": "Cold"}
            ],
            "interactions": [
                {"InteractionID": "301", "LeadID": "201", "Type": "Email"}
            ]
        }
    
    def test_find_contacts_by_company(self):
        result = self.ld.find("contacts", CompanyID="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Name"], "John Doe")
    
    def test_find_one_company(self):
        company = self.ld.find_one("companies", CompanyID="1")
        self.assertIsNotNone(company)
        self.assertEqual(company["Name"], "TechCorp")
    
    def test_get_company_contacts(self):
        contacts = self.ld.get_company_contacts(1)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["Name"], "John Doe")
    
    def test_find_no_results(self):
        result = self.ld.find("contacts", CompanyID="999")
        self.assertEqual(result, [])
    
    def test_contacts_with_company(self):
        result = self.ld.get_contacts_with_company()
        self.assertEqual(result[0]["CompanyName"], "TechCorp")
    
    def test_get_full_lead(self):

        expected = {
            "lead": {"LeadID": "201", "CompanyID": "1", "Status": "Hot"},
            "company": {"CompanyID": "1", "Name": "TechCorp"},
            "contacts": [
            {"ContactID": "101", "Name": "John Doe", "CompanyID": "1"}
            ],
            "interactions": [
            {"InteractionID": "301", "LeadID": "201", "Type": "Email"}
            ]
                }
        result = self.get_full_lead()

        self.assertEqual(result, expected)
    
    if __name__ == "__main__":
        unittest.main()