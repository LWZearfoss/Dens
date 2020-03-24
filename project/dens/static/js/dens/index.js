const index = new Vue({
	el: "#index",
	data: {
		"user_id": $('#user_id').val(),
		"url": $('#url').val(),
		"dens": [],
		"den_name": "",
		"errors": [],
	},
	created: function () {
		this.connect();
	},
	mounted: function () {
		$(this.$el).foundation();
	},
	methods: {
		async connect() {
			this.socket = new WebSocket((window.location.protocol == "https:" ? "wss" : "ws") + "://" + window.location.host + "/ws/index/");
			this.socket.onopen = () => {
				this.socket.onmessage = (data) => {
					var response = JSON.parse(data.data);
					if (response['data']['dens']) {
						this.dens = response['data']['dens'];
					} else {
						this.errors = response['data']['errors']
					}
				};
			};
			this.socket.onclose = (e) => {
				switch (e.code) {
					case 1000:
						break;
					default:
						setTimeout(function () {
							index.connect();
						}, 1000);
						break;
				}
			};
		},
		async createDen() {
			this.socket.send(JSON.stringify({
				'create': true,
				'den_name': this.den_name,
			}));
			this.den_name = '';
		},
		async deleteDen(den_id) {
			this.socket.send(JSON.stringify({
				'create': false,
				'den_id': den_id,
			}));
		},
	},
});