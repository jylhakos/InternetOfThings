import { StatusBar } from 'expo-status-bar';

import { StyleSheet, Text, TextInput, Button, View, FlatList, ActivityIndicator } from 'react-native';

import React, { useState, useEffect } from 'react';

import axios from 'axios';

export default function App() {

  const [isLoading, setLoading] = useState(true);

  const [data, setData] = useState([]);

  const [values, setValues] = useState({ 
    artist: '', 
    title: '', 
    price: ''
  });

  const handleChangeText = (name, value) => {
    setValues({
      ...values,
      [name]: value,
    });
  };

  const handleSubmit = () => console.log('handleSubmit', values);

  const getAlbums = async () => {

    try {
        const response = await axios.get('http://localhost:8001/albums');
        //alert(JSON.stringify(response.data));
        console.log('getAlbums',response.data)
        setData(response.data);
      } catch (error) {
        alert(error.message);
      } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    getAlbums();
  }, []);

  return (
    <View style={styles.container}>
      <Text>Albums</Text>
      {isLoading ? <ActivityIndicator/> : (
        <FlatList
          data={data}
          keyExtractor={({ id }, index) => id}
          renderItem={({ item }) => (
            <Text>
            {item.id}
            {item.artist}
            {item.title}
            {item.price}
            </Text>
          )}
        />
      )}

      <TextInput
        placeholder="Artist"
        name="artist"
        value={values.artist}
        onChangeText={(text) => handleChangeText('artist', text)}
        style={styles.input}
      />

      <TextInput
        placeholder="Title"
        name="title"
        value={values.title}
        onChangeText={(text) => handleChangeText('title', text)}
        style={styles.input}
      />

      <TextInput
        placeholder="Price"
        name="price"
        value={values.price}
        onChangeText={(text) => handleChangeText('price', text)}
        style={styles.input}
        keyboardType="numeric"
      />

      <Button onPress={handleSubmit} title="Submit" />

      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
  },
  input: {
      margin: 15,
      height: 40,
      borderColor: 'blue',
      borderWidth: 1
   },
});