import { StatusBar } from 'expo-status-bar';

import { StyleSheet, Text, TextInput, Button, View, FlatList, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';

import React, { useState, useEffect } from 'react';

import axios from 'axios';

const Item = ({ item, onPress, backgroundColor, textColor }) => (
  <TouchableOpacity onPress={onPress} style={[styles.item, backgroundColor]}>
    <Text style={[styles.title, textColor]}>{item.artist} {item.title} {item.price}</Text>
  </TouchableOpacity>
);

const ItemTest = ({ item }) => (
  <View style={styles.item}>
    <Text style={styles.content}>{item.artist} {item.title} {item.price}</Text>
  </View>
);

export default function App() {

  const [isLoading, setLoading] = useState(true);

  const [data, setData] = useState([]);

  const [values, setValues] = useState({ artist: '', title: '', price: '' });

  const [selectedId, setSelectedId] = useState(null);

  const handleChangeText = (name, value) => {
    setValues({
      ...values,
      [name]: value,
    });
  };

  const handleSubmit = () => { 
    console.log('handleSubmit', values);
    addAlbums(values.artist, values.title, values.price);
  }

  const getAlbums = async () => {

    try {
        const response = await axios.get('http://localhost:8001/albums');
        //alert(JSON.stringify(response.data));
        console.log('getAlbums', response.data)
        setData(response.data);
      } catch (error) {
        alert(error.message);
      } finally {
        setLoading(false);
    }
  };

  const addAlbums = async (artist, title, price) => {

    try {

        const album = {
            "title": title,
            "artist": artist,
            "price": parseFloat(price)
          };

        console.log('album', album);

        const response = await axios.post('http://localhost:8001/albums', 
          album, 
          { headers:
            { 'Content-Type': 'application/json' }
          });

        console.log('response.data', response.data);

        if (data && data.length)
          setData([response.data, ...data]);
        else {
          setData([response.data]);
        }

        setValues({artist: '', title: '', price: ''});

      } catch (error) {

        alert(error.message);

      }
  };

  useEffect(() => {
    getAlbums();
  }, []);

  const renderItem = ({ item }) => {

    const backgroundColor = item.id === selectedId ? "#6e3b6e" : "#f9c2ff";
    
    const color = item.id === selectedId ? 'white' : 'black';

    console.log('selectedId', selectedId);

    return (
      <Item
        item={item}
        onPress={() => setSelectedId(item.id)}
        backgroundColor={{ backgroundColor }}
        textColor={{ color }}
      />
    );
  };

  return (
    <SafeAreaView style={styles.container}>

      <Text style={styles.header}>Albums</Text>

      {isLoading ? <ActivityIndicator/> : (
        <FlatList
          data={data}
          keyExtractor={({ id }, index) => id}
          renderItem={renderItem}
          extraData={selectedId}
        />
      )}

      <View style={styles.container}>

        <Text style={styles.header}>Add Album</Text>

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
        
      </View>

      <StatusBar style="auto" />

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  item: {
    backgroundColor: '#f9c2ff',
    padding: 4,
    marginVertical: 2,
    marginHorizontal: 4,
  },
  header: {
    fontSize: 24,
    padding: 4,
  },
  content: {
    fontSize: 18,
    padding: 2,
  },
  input: {
      margin: 8,
      height: 24,
      borderColor: '#f9c2ff',
      borderWidth: 1
   },
});
