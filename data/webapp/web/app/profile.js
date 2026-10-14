var AppProfile = {
  container: null,
  getContainer: function() {
    // if (this.container != null) {
    //   return this.container;
    // } 
    this.container = document.createElement("div");

    // draw the top title
    this.container.append(AppTopTitle.getContainer('<i class="fa fa-user"></i> Profile'));


    return this.container;
  }
};