var Gujarat = [
  "Ahmedabad",
  "Amreli",
  "Anand",
  "Aravalli",
  "Banaskantha",
  "Bharuch",
  "Bhavnagar",
  "Botad",
  "Chhota Udaipur",
  "Dahod",
  "Dang",
  "Devbhoomi Dwarka",
  "Gandhinagar",
  "Gir Somnath",
  "Jamnagar",
  "Junagadh",
  "Kheda",
  "Kutch",
  "Mahisagar",
  "Mehsana",
  "Morbi",
  "Narmada",
  "Navsari",
  "Panchmahal",
  "Patan",
  "Porbandar",
  "Rajkot",
  "Sabarkantha",
  "Surat",
  "Surendranagar",
  "Tapi",
  "Vadodara",
  "Valsad",
];
var Maharashtra = [
  "Ahmednagar",
  "Akola",
  "Amravati",
  "Aurangabad",
  "Beed",
  "Bhandara",
  "Buldhana",
  "Chandrapur",
  "Dhule",
  "Gadchiroli",
  "Gondia",
  "Hingoli",
  "Jalgaon",
  "Jalna",
  "Kolhapur",
  "Latur",
  "Mumbai City",
  "Mumbai Suburban",
  "Nagpur",
  "Nanded",
  "Nandurbar",
  "Nashik",
  "Osmanabad",
  "Palghar",
  "Parbhani",
  "Pune",
  "Raigad",
  "Ratnagiri",
  "Sangli",
  "Satara",
  "Sindhudurg",
  "Solapur",
  "Thane",
  "Wardha",
  "Washim",
  "Yavatmal",
];
var Delhi = [
  "Central Delhi",
  "East Delhi",
  "New Delhi",
  "North Delhi",
  "North East Delhi",
  "North West Delhi",
  "Shahdara",
  "South Delhi",
  "South East Delhi",
  "South West Delhi",
  "West Delhi",
];

$("inputState").change(function () {
  var StateSelected = $(this).val();
  var optionsList;
  var htmlString = "";

  switch (StateSelected) {
    case "Gujarat":
      optionsList = Gujarat;
      break;
    case "Maharashtra":
      optionsList = Maharashtra;
      break;
    case "Delhi":
      optionsList = Delhi;
      break;
    default:
      optionsList = [];
  }

  for (var i = 0; i < optionsList.length; i++) {
    htmlString =
      htmlString +
      "<option value='" +
      optionsList[i] +
      "'>" +
      optionsList[i] +
      "</option>";
  }
  $("inputDistrict").html(htmlString);
});
