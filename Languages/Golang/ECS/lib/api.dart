import 'package:http/http.dart' as http;
import 'dart:convert';

const baseUrl = 'https://api.example.com/api';

Future<List<dynamic>> getItems() async {
  final response = await http.get(Uri.parse('$baseUrl/items'));
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to load items');
  }
}

// Add similar functions for POST, PUT, DELETE