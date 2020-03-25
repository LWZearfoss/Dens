const den = new Vue({
	el: "#den",
	data: {
		"protocol": window.location.protocol + '//',
		"path": window.location.host,
		"den_slug": $('#den_slug').val(),
		"user_id": $('#user_id').val(),
		"den_name": "",
		"messages": [],
		"text": "",
		"attachment": "",
		"errors": [],
		"image_formats": new Set(["apng", "bmp", "gif", "ico", "cur", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png", "svg", "tif", "tiff", "webp"]),
		"audio_formats": new Set(["mp3", "mpeg", "wav"]),
		"video_formats": new Set(["mp4", "ogg", "webm"]),
	},
	created: function () {
		this.connect();
	},
	mounted: function () {
		$(this.$el).foundation();
	},
	updated: function () {
		if (this.messages.length > 0) {
			setTimeout(() => {
				if ($(window).scrollTop() + $(window).height() >= $(document).height() - this.$refs.chat[this.messages.length - 1].clientHeight - 100) {
					window.scrollTo({
						top: document.body.scrollHeight,
						behavior: 'smooth',
					});
				}
			}, 1000);
		}
	},
	methods: {
		async connect() {
			this.socket = new WebSocket((this.protocol == "https://" ? "wss" : "ws") + "://" + this.path + "/ws/den/" + this.den_slug + "/");
			this.socket.onopen = () => {
				this.socket.onmessage = (data) => {
					var response = JSON.parse(data.data);
					if (response['data']['messages']) {
						this.den_name = response['data']['den_name'];
						this.messages = response['data']['messages'];
					} else if (response['data']['errors']) {
						this.errors = response['data']['errors'];
					} else {
						this.socket.close(4000);
						window.location.replace(this.protocol + this.path);
					}

				};
			};
			this.socket.onclose = (e) => {
				switch (e.code) {
					case 4000:
						break;
					default:
						setTimeout(function () {
							den.connect();
						}, 1000);
						break;
				}
			};
			setTimeout(() => {
				document.title = "Den - " + this.den_name;
				window.scrollTo({
					top: document.body.scrollHeight,
					behavior: 'smooth',
				});
			}, 5000);
		},
		// Adapted from https://stackoverflow.com/questions/36280818/how-to-convert-file-to-base64-in-javascript
		async toBase64(attachment) {
			return new Promise((resolve, reject) => {
				const reader = new FileReader();
				reader.readAsDataURL(attachment);
				reader.onload = () => resolve(reader.result);
				reader.onerror = error => reject(error);
			});
		},
		async handleFile() {
			if (this.$refs.attachment.files[0]) {
				this.attachment = zlib_encode(await this.toBase64(this.$refs.attachment.files[0]));
			} else {
				this.attachment = '';
			}
		},
		async createMessage() {
			if (this.attachment && this.$refs.attachment.files[0].size > 52428800) {
				this.errors.push("The attachment must not be larger than 50MB.")
			} else {
				this.socket.send(JSON.stringify({
					'create': true,
					'text': this.text,
					'attachment': this.attachment,
					'attachment_name': this.attachment ? this.$refs.attachment.files[0].name : '',
				}));
			}
			this.text = '';
			this.attachment = ''
			this.$refs.attachment.value = ''
			window.scrollTo({
				top: document.body.scrollHeight,
				behavior: 'auto',
			});
		},
		async deleteMessage(message_id) {
			this.socket.send(JSON.stringify({
				'create': false,
				'message_id': message_id,
			}));
		},
	},
});