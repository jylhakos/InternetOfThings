import { Component, OnInit } from '@angular/core';
import { ApiService, Device } from './api.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  devices: Device[] = [];
  errorMessage: string = '';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.fetchDevices();
  }

  fetchDevices(): void {
    this.apiService.getDevices().subscribe({
      next: (data) => {
        this.devices = data;
      },
      error: (error) => {
        this.errorMessage = 'Error fetching devices: ' + error.message;
        console.error('There was an error', error);
      }
    });
  }
}