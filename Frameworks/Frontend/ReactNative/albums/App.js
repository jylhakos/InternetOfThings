import { StatusBar } from 'expo-status-bar';

import { StyleSheet, Text, View, FlatList, ActivityIndicator } from 'react-native';

import React, { useState, useEffect } from 'react';

import axios from 'axios';

export default function App() {

  const [isLoading, setLoading] = useState(true);

  const [data, setData] = useState([]);

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
            <Text>{item.id}, {item.artist}, {item.title}, {item.price}</Text>
          )}
        />
      )}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});