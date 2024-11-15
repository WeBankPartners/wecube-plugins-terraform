current_dir=$(shell pwd)
version=$(PLUGIN_VERSION)
project_dir=$(shell basename "${current_dir}")

clean:
	rm -rf terraform-server/terraform-server
	rm -rf ui/dist
	rm -rf ui/plugin

build: clean
	chmod +x ./build/*.sh
	docker run --rm -v $(current_dir):/go/src/github.com/WeBankPartners/$(project_dir) --name build_$(project_dir) ccr.ccs.tencentyun.com/webankpartners/golang-ext:v1.15.6 /bin/bash /go/src/github.com/WeBankPartners/$(project_dir)/build/build-server.sh
	./build/build-ui.sh $(current_dir)

image: build
	docker build -t $(project_dir):$(version) .

package: image
	mkdir -p plugin
	cp -r ui/dist/* plugin/
	zip -r ui.zip plugin
	rm -rf plugin
	cp build/register.xml ./
	cp wiki/init.sql ./init.sql
	cat wiki/terraform.sql >> ./init.sql
	sed -i "s~{{PLUGIN_VERSION}}~$(version)~g" ./register.xml
	sed -i "s~{{REPOSITORY}}~$(project_dir)~g" ./register.xml
	docker save -o image.tar $(project_dir):$(version)
	zip  $(project_dir)-$(version).zip image.tar init.sql register.xml ui.zip
	rm -f register.xml init.sql ui.zip
	rm -rf ./*.tar
	docker rmi $(project_dir):$(version)

upload: package
	$(eval container_id:=$(shell docker run -v $(current_dir):/package -itd --entrypoint=/bin/sh minio/mc))
	docker exec $(container_id) mc config host add wecubeS3 $(s3_server_url) $(s3_access_key) $(s3_secret_key) wecubeS3
	docker exec $(container_id) mc cp /package/$(project_dir)-$(version).zip wecubeS3/wecube-plugin-package-bucket
	docker rm -f $(container_id)
	rm -rf $(project_dir)-$(version).zip